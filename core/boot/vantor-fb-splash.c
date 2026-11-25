/*
 * VANTOR Genesis framebuffer splash.
 * Small fbdev renderer: no X11, DRM userspace, fonts, or image assets.
 * Supports packed true-colour 16/24/32bpp framebuffers.
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <linux/fb.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

static int fd = -1;
static uint8_t *fb;
static size_t fb_len;
static struct fb_fix_screeninfo fix;
static struct fb_var_screeninfo var;
static unsigned progress = 8;

static const uint8_t font[27][5] = {
 {0x7e,0x11,0x11,0x11,0x7e}, {0x7f,0x49,0x49,0x49,0x36},
 {0x3e,0x41,0x41,0x41,0x22}, {0x7f,0x41,0x41,0x22,0x1c},
 {0x7f,0x49,0x49,0x49,0x41}, {0x7f,0x09,0x09,0x09,0x01},
 {0x3e,0x41,0x49,0x49,0x7a}, {0x7f,0x08,0x08,0x08,0x7f},
 {0x00,0x41,0x7f,0x41,0x00}, {0x20,0x40,0x41,0x3f,0x01},
 {0x7f,0x08,0x14,0x22,0x41}, {0x7f,0x40,0x40,0x40,0x40},
 {0x7f,0x02,0x0c,0x02,0x7f}, {0x7f,0x04,0x08,0x10,0x7f},
 {0x3e,0x41,0x41,0x41,0x3e}, {0x7f,0x09,0x09,0x09,0x06},
 {0x3e,0x41,0x51,0x21,0x5e}, {0x7f,0x09,0x19,0x29,0x46},
 {0x46,0x49,0x49,0x49,0x31}, {0x01,0x01,0x7f,0x01,0x01},
 {0x3f,0x40,0x40,0x40,0x3f}, {0x1f,0x20,0x40,0x20,0x1f},
 {0x3f,0x40,0x38,0x40,0x3f}, {0x63,0x14,0x08,0x14,0x63},
 {0x07,0x08,0x70,0x08,0x07}, {0x61,0x51,0x49,0x45,0x43},
 {0,0,0,0,0}
};

static void pixel(int x, int y, uint8_t r, uint8_t g, uint8_t b) {
    if (x < 0 || y < 0 || (unsigned)x >= var.xres || (unsigned)y >= var.yres) return;
    unsigned bytes = var.bits_per_pixel / 8;
    if (bytes < 2 || bytes > 4) return;
    size_t off = (size_t)(y + var.yoffset) * fix.line_length +
                 (size_t)(x + var.xoffset) * bytes;
    if (off + bytes > fb_len) return;
    uint32_t v = 0;
    v |= ((uint32_t)r >> (8 - var.red.length)) << var.red.offset;
    v |= ((uint32_t)g >> (8 - var.green.length)) << var.green.offset;
    v |= ((uint32_t)b >> (8 - var.blue.length)) << var.blue.offset;
    if (var.bits_per_pixel == 16) *(uint16_t *)(fb + off) = (uint16_t)v;
    else if (var.bits_per_pixel == 24) {
        fb[off] = (uint8_t)v; fb[off+1] = (uint8_t)(v>>8); fb[off+2] = (uint8_t)(v>>16);
    } else *(uint32_t *)(fb + off) = v;
}

static void rect(int x, int y, int w, int h, uint8_t r, uint8_t g, uint8_t b) {
    for (int yy=y; yy<y+h; yy++) for (int xx=x; xx<x+w; xx++) pixel(xx,yy,r,g,b);
}
static void line(int x0,int y0,int x1,int y1,int width,uint8_t r,uint8_t g,uint8_t b) {
    int dx=abs(x1-x0), sx=x0<x1?1:-1, dy=-abs(y1-y0), sy=y0<y1?1:-1, err=dx+dy;
    for (;;) {
        for(int oy=-width;oy<=width;oy++) for(int ox=-width;ox<=width;ox++)
            if(ox*ox+oy*oy<=width*width) pixel(x0+ox,y0+oy,r,g,b);
        if(x0==x1 && y0==y1) break;
        int e2=2*err; if(e2>=dy){err+=dy;x0+=sx;} if(e2<=dx){err+=dx;y0+=sy;}
    }
}
static void text(const char *s,int x,int y,int scale,uint8_t r,uint8_t g,uint8_t b) {
    for(;*s;s++,x+=6*scale) {
        char c=*s;
        if(c>='a'&&c<='z') c-=32;
        if(c>='A'&&c<='Z') {
            const uint8_t *glyph=font[c-'A'];
            for(int col=0;col<5;col++) for(int row=0;row<7;row++)
                if(glyph[col]&(1u<<row)) rect(x+col*scale,y+row*scale,scale,scale,r,g,b);
        } else if(c=='.') rect(x,y+6*scale,scale,scale,r,g,b);
        else if(c=='-') rect(x,y+3*scale,4*scale,scale,r,g,b);
        else if(c==':') {rect(x,y+2*scale,scale,scale,r,g,b);rect(x,y+5*scale,scale,scale,r,g,b);}
    }
}
static void background(void) {
    for(unsigned y=0;y<var.yres;y++) {
        uint8_t r=7+(uint8_t)(y*3/(var.yres?var.yres:1));
        uint8_t g=19+(uint8_t)(y*10/(var.yres?var.yres:1));
        uint8_t b=33+(uint8_t)(y*19/(var.yres?var.yres:1));
        rect(0,(int)y,(int)var.xres,1,r,g,b);
    }
    for(int i=0;i<34;i++) {
        int x=(i*197+71)%(int)var.xres, y=(i*113+29)%(int)var.yres;
        pixel(x,y,35,81,116);
    }
}
static void draw_orbit(int cx,int cy,int rx,int ry,double angle) {
    for(int d=0;d<360;d++) {
        double a=d*3.141592653589793/180.0;
        int x=cx+(int)(rx*cos(a)), y=cy+(int)(ry*sin(a));
        pixel(x,y,0,92,142);
        if(d%2==0) pixel(x,y,0,160,205);
    }
    int dx=cx+(int)(rx*cos(angle)), dy=cy+(int)(ry*sin(angle));
    for(int oy=-4;oy<=4;oy++) for(int ox=-4;ox<=4;ox++)
        if(ox*ox+oy*oy<=16) pixel(dx+ox,dy+oy,0,220,255);
}
static void render(unsigned pct,const char *status,double angle) {
    background();
    int cx=(int)var.xres/2, cy=(int)var.yres*34/100;
    int unit=(int)(var.yres/180); if(unit<1) unit=1;
    int rx=(int)var.xres/5, ry=(int)var.yres/12;
    draw_orbit(cx,cy,rx,ry,angle);
    /* Metallic V emblem, with a cyan inner edge. */
    line(cx-42*unit,cy-36*unit,cx,cy+45*unit,8*unit,188,211,232);
    line(cx,cy+45*unit,cx+42*unit,cy-36*unit,8*unit,188,211,232);
    line(cx-33*unit,cy-31*unit,cx,cy+31*unit,2*unit,0,207,255);
    line(cx,cy+31*unit,cx+33*unit,cy-31*unit,2*unit,0,207,255);
    int title_scale=var.xres<800?2:3;
    const char *title="VANTOR LINUX";
    text(title,cx-(int)strlen(title)*3*title_scale,cy+ry+18*unit,title_scale,244,248,255);
    const char *slogan="ONE SYSTEM EVERY GENERATION";
    text(slogan,cx-(int)strlen(slogan)*3,cy+ry+45*unit,1,0,207,255);
    int barw=(int)var.xres*58/100, barh=8*unit, bx=cx-barw/2, by=(int)var.yres*82/100;
    rect(bx,by,barw,barh,28,54,77);
    rect(bx,by,(barw*(int)pct)/100,barh,0,207,255);
    text(status,cx-(int)strlen(status)*3,by+18*unit,1,155,176,200);
}
static int open_fb(void) {
    fd=open("/dev/fb0",O_RDWR);
    if(fd<0) return -1;
    if(ioctl(fd,FBIOGET_FSCREENINFO,&fix)<0 || ioctl(fd,FBIOGET_VSCREENINFO,&var)<0) return -1;
    if(var.bits_per_pixel!=16 && var.bits_per_pixel!=24 && var.bits_per_pixel!=32) return -1;
    if(var.red.length==0 || var.green.length==0 || var.blue.length==0) return -1;
    fb_len=(size_t)fix.line_length*(var.yres+var.yoffset);
    fb=mmap(NULL,fb_len,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
    return fb==MAP_FAILED ? -1 : 0;
}
static void close_fb(void) {
    if(fb && fb!=MAP_FAILED) { msync(fb,fb_len,MS_SYNC); munmap(fb,fb_len); }
    if(fd>=0) close(fd);
}
static void delay_ms(long ms) { struct timespec t={ms/1000,(ms%1000)*1000000}; nanosleep(&t,NULL); }

int main(int argc,char **argv) {
    const char *cmd=argc>1?argv[1]:"start";
    if(open_fb()<0) { close_fb(); return 1; }
    if(!strcmp(cmd,"start")) {
        for(int i=0;i<18;i++) { render(8+(unsigned)i/3,"INITIALIZING VANTOR",i*0.34); delay_ms(55); }
        progress=18;
    } else if(!strcmp(cmd,"step")) {
        progress+=22; if(progress>94) progress=94;
        render(progress,argc>2?argv[2]:"STARTING SYSTEM",1.2);
    } else if(!strcmp(cmd,"finish")) {
        rect(0,0,(int)var.xres,(int)var.yres,0,0,0);
    } else { close_fb(); return 2; }
    close_fb();
    return 0;
}
