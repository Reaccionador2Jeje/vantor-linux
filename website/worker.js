const SECURITY_HEADERS = {
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
};

const SITE_HTML = `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#071321">
<meta name="description" content="VANTOR Linux: distribución Linux independiente, base independiente y objetivo universal. ONE SYSTEM. EVERY GENERATION.">
<meta property="og:title" content="VANTOR Linux — One System. Every Generation.">
<meta property="og:description" content="Un sistema independiente que conecta generaciones de hardware.">
<meta property="og:type" content="website">
<title>VANTOR Linux — One System. Every Generation.</title>
<style>
:root{color-scheme:dark;--bg:#071321;--surface:#0c1d30;--raised:#132a43;--line:#24435f;--cyan:#00cfff;--blue:#0877ff;--metal:#b9cce3;--text:#f4f8ff;--muted:#9bb0c8;--green:#42d6a4;--yellow:#ffc857;--radius:18px;--display:Orbitron,"Arial",sans-serif;--ui:Rajdhani,"Noto Sans",system-ui,sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:86px}body{margin:0;background:var(--bg);color:var(--text);font:17px/1.65 var(--ui);overflow-x:hidden}body:before{content:"";position:fixed;inset:0;pointer-events:none;z-index:-1;background:radial-gradient(ellipse at 80% -10%,#0877ff24,transparent 38%),radial-gradient(ellipse at 0% 42%,#00cfff0b,transparent 35%)}a{color:var(--cyan);text-decoration:none}a:hover{color:#fff}button,a{ -webkit-tap-highlight-color:transparent}button:focus-visible,a:focus-visible{outline:2px solid var(--cyan);outline-offset:4px}.wrap{width:min(1160px,calc(100% - 40px));margin:auto}.topline{height:3px;background:linear-gradient(90deg,var(--blue),var(--cyan),transparent)}header{position:sticky;top:0;z-index:20;background:#071321eF;border-bottom:1px solid #ffffff16;backdrop-filter:blur(16px)}.nav{height:76px;display:flex;align-items:center;justify-content:space-between;gap:24px}.brand{display:flex;align-items:center;gap:12px;color:var(--text);font:800 15px var(--display);letter-spacing:.13em}.brand img{width:42px;height:42px}.navlinks{display:flex;gap:24px;align-items:center}.navlinks a{font-weight:700;color:var(--muted);font-size:15px}.navlinks a:hover{color:var(--cyan)}.nav-cta,.button{display:inline-flex;align-items:center;justify-content:center;gap:9px;border:1px solid #00cfff88;border-radius:999px;padding:11px 18px;color:var(--text);font-weight:800;background:linear-gradient(120deg,#0877ff35,#00cfff18);transition:transform .2s,border-color .2s}.nav-cta:hover,.button:hover{transform:translateY(-2px);border-color:var(--cyan);color:#fff}.menu{display:none;border:1px solid var(--line);background:var(--surface);color:var(--text);border-radius:10px;padding:9px 12px;font-size:20px}.hero{padding:90px 0 76px;position:relative}.hero-grid{display:grid;grid-template-columns:1.15fr .85fr;gap:48px;align-items:center}.eyebrow{color:var(--cyan);font:800 12px var(--display);letter-spacing:.19em;text-transform:uppercase}.hero h1{font:800 clamp(42px,7vw,82px)/1.04 var(--display);letter-spacing:-.055em;margin:22px 0 18px}.hero h1 span{background:linear-gradient(90deg,var(--cyan),#7eaeff);background-clip:text;color:transparent}.lead{font-size:21px;color:var(--muted);max-width:670px}.actions{display:flex;gap:12px;flex-wrap:wrap;margin:30px 0}.button.primary{background:linear-gradient(110deg,#0877ff,#00aee8);border-color:transparent;color:#031323}.button.secondary{background:transparent;border-color:var(--line)}.hero-art{min-height:380px;display:grid;place-items:center;position:relative}.hero-art:before{content:"";position:absolute;width:300px;height:300px;border-radius:50%;background:#0877ff22;filter:blur(55px)}.emblem{width:min(100%,390px);filter:drop-shadow(0 0 35px #00cfff28);position:relative}.hero-meta{display:flex;gap:22px;flex-wrap:wrap;color:var(--muted);font-size:14px}.hero-meta span:before{content:"◆";color:var(--cyan);font-size:9px;margin-right:8px}.statusbar{border:1px solid #ffc85755;background:#ffc8570c;border-radius:13px;padding:13px 17px;display:flex;gap:12px;align-items:center;color:var(--muted);font-size:14px;margin-top:24px}.statusbar b{color:var(--yellow);font-size:12px;letter-spacing:.1em}.section{padding:82px 0;border-top:1px solid #ffffff12}.section-head{max-width:720px;margin-bottom:34px}.kicker{font:800 11px var(--display);letter-spacing:.18em;color:var(--cyan);text-transform:uppercase}.section h2{font:800 clamp(29px,4vw,46px)/1.15 var(--display);margin:12px 0}.section-head p,.muted{color:var(--muted)}.grid{display:grid;gap:16px}.grid.four{grid-template-columns:repeat(4,1fr)}.grid.three{grid-template-columns:repeat(3,1fr)}.card{background:linear-gradient(145deg,#132a43d9,#0c1d30e8);border:1px solid #ffffff18;border-radius:var(--radius);padding:24px;min-width:0}.card .number{color:var(--cyan);font:800 12px var(--display);letter-spacing:.12em}.card h3{font:800 20px var(--display);margin:12px 0 8px}.card p{color:var(--muted);margin:0}.iconbox{width:42px;height:42px;display:grid;place-items:center;border-radius:12px;background:#00cfff12;border:1px solid #00cfff33;color:var(--cyan);font-size:21px;margin-bottom:18px}.edition{position:relative;overflow:hidden}.edition:after{content:"";position:absolute;width:150px;height:150px;border-radius:50%;right:-80px;top:-80px;background:#0877ff22;filter:blur(12px)}.edition .arch{font:800 11px var(--display);color:var(--cyan);letter-spacing:.14em}.tag{display:inline-block;border:1px solid #42d6a455;color:var(--green);border-radius:999px;padding:4px 9px;font-size:11px;font-weight:800;margin-top:15px}.tag.pending{border-color:#ffc85766;color:var(--yellow)}.split{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:stretch}.specs{display:grid;grid-template-columns:1fr 1fr;gap:10px}.spec{padding:15px;border:1px solid #ffffff17;background:#0c1d30;border-radius:12px}.spec b{display:block;color:var(--text);font:700 16px var(--display)}.spec span{color:var(--muted);font-size:13px}.terminal{background:#030b13;border:1px solid #1c3b57;border-radius:16px;overflow:hidden;box-shadow:0 20px 70px #0005}.terminal-top{padding:12px 16px;border-bottom:1px solid #ffffff16;display:flex;gap:7px;align-items:center;color:var(--muted);font-size:12px}.dot{width:8px;height:8px;border-radius:50%;background:#35516a}.terminal pre{margin:0;padding:22px;white-space:pre-wrap;overflow-wrap:anywhere;color:#d6e8f8;font:13px/1.8 ui-monospace,monospace}.terminal code{color:var(--cyan)}.copyhint{color:var(--muted);font-size:12px;padding:0 22px 16px}.list{list-style:none;padding:0;margin:18px 0}.list li{padding:10px 0;border-bottom:1px solid #ffffff12;color:var(--muted)}.list li:before{content:"✓";color:var(--green);font-weight:900;margin-right:10px}.list li.pending:before{content:"◷";color:var(--yellow)}.mirror{border:1px solid #00cfff55;background:linear-gradient(120deg,#0877ff16,#00cfff08);border-radius:18px;padding:28px}.endpoint{display:block;background:#030b13;border:1px solid #ffffff12;border-radius:9px;padding:11px 13px;margin:9px 0;color:var(--cyan);font:12px ui-monospace,monospace;overflow-wrap:anywhere}.docs-grid a{display:block;color:var(--text);font-weight:800;margin-top:12px}.docs-grid a span{color:var(--cyan);float:right}.footer{padding:38px 0 50px;border-top:1px solid #ffffff16;color:var(--muted);font-size:13px}.footer-grid{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}.footer strong{color:var(--text);font-family:var(--display);letter-spacing:.1em}.backtop{position:fixed;right:20px;bottom:20px;border:1px solid var(--line);border-radius:50%;width:42px;height:42px;background:var(--surface);color:var(--cyan);font-size:20px;cursor:pointer;display:none}
@media(max-width:900px){.hero-grid{grid-template-columns:1fr .7fr;gap:18px}.grid.four{grid-template-columns:repeat(2,1fr)}.grid.three{grid-template-columns:repeat(2,1fr)}.navlinks{gap:14px}.hero-art{min-height:280px}}
@media(max-width:680px){.wrap{width:min(100% - 28px,560px)}.nav{height:66px}.brand{font-size:12px}.brand img{width:36px;height:36px}.menu{display:block}.navlinks{display:none;position:absolute;left:14px;right:14px;top:72px;padding:18px;background:var(--surface);border:1px solid var(--line);border-radius:14px;flex-direction:column;align-items:stretch;gap:15px}.navlinks.open{display:flex}.navlinks a{padding:5px}.nav-cta{display:none}.hero{padding:54px 0 52px}.hero-grid{grid-template-columns:1fr}.hero-art{min-height:230px;grid-row:1}.emblem{width:240px}.hero h1{font-size:clamp(38px,12vw,58px);margin-top:14px}.lead{font-size:18px}.section{padding:60px 0}.grid.three,.grid.four,.split{grid-template-columns:1fr}.specs{grid-template-columns:1fr 1fr}.statusbar{align-items:flex-start;flex-direction:column}.footer-grid{flex-direction:column}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*:before,*:after{transition:none!important;animation:none!important}}
</style>
</head>
<body>
<div class="topline"></div>
<header>
 <div class="wrap nav">
  <a class="brand" href="#inicio" aria-label="VANTOR Linux, inicio"><img src="/assets/vantor-mark.svg" alt="">VANTOR LINUX</a>
  <nav class="navlinks" id="navlinks" aria-label="Navegación principal">
   <a href="#sistema">Sistema</a><a href="#ediciones">Ediciones</a><a href="#arquitectura">Arquitectura</a><a href="#instalar">Empezar</a><a href="#documentacion">Documentación</a>
  </nav>
  <a class="nav-cta" href="https://github.com/Reaccionador2Jeje/vantor-linux">Ver en GitHub ↗</a>
  <button class="menu" id="menu" aria-label="Abrir menú" aria-expanded="false">☰</button>
 </div>
</header>
<main id="inicio">
<section class="hero wrap">
 <div class="hero-grid">
  <div>
   <div class="eyebrow">Independent Linux · Genesis</div>
   <h1>ONE SYSTEM.<br><span>EVERY GENERATION.</span></h1>
   <p class="lead">Un sistema operativo independiente, construido desde sus cimientos. Una plataforma abierta que busca conectar distintas generaciones de hardware bajo una identidad propia.</p>
   <div class="actions">
    <a class="button primary" href="https://github.com/Reaccionador2Jeje/vantor-linux">Explorar el proyecto ↗</a>
    <a class="button secondary" href="#instalar">Cómo empezar ↓</a>
   </div>
   <div class="hero-meta"><span>Base independiente</span><span>Gestión Nyan</span><span>Open source</span></div>
   <div class="statusbar"><b>FASE GENESIS · EN DESARROLLO</b><span>El arranque de las imágenes ISO y la compatibilidad de hardware siguen en validación. No se presenta todavía como una versión estable.</span></div>
  </div>
  <div class="hero-art" aria-label="Emblema VANTOR">
   <svg class="emblem" viewBox="0 0 512 512" role="img" aria-labelledby="marktitle">
    <title id="marktitle">Emblema oficial de VANTOR</title>
    <defs><linearGradient id="m" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f4fbff"/><stop offset=".5" stop-color="#9db6d3"/><stop offset="1" stop-color="#7189a8"/></linearGradient><linearGradient id="c" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#00d9ff"/><stop offset="1" stop-color="#0877ff"/></linearGradient><filter id="g"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
    <circle cx="256" cy="256" r="220" fill="#0c1d30" stroke="#24435f" stroke-width="2"/>
    <ellipse cx="256" cy="256" rx="220" ry="88" fill="none" stroke="url(#c)" stroke-width="13" transform="rotate(-24 256 256)" filter="url(#g)"/>
    <path d="M104 105h100l52 181 52-181h100L282 407h-52z" fill="url(#m)" stroke="#d8f5ff" stroke-width="5" stroke-linejoin="round"/>
    <path d="M256 286l26 121h-52z" fill="#00bff3" opacity=".72"/>
    <path d="M91 286c38 59 93 91 139 104" fill="none" stroke="#00d9ff" stroke-width="8" stroke-linecap="round" filter="url(#g)"/>
   </svg>
  </div>
 </div>
</section>

<section class="section" id="sistema"><div class="wrap">
 <div class="section-head"><div class="kicker">01 / El sistema</div><h2>Una distribución con identidad propia.</h2><p>VANTOR no pretende ser una capa visual sobre otra distribución. Su objetivo es construir una base independiente, con herramientas y decisiones técnicas documentadas en el propio proyecto.</p></div>
 <div class="grid four">
  <article class="card"><div class="iconbox">◇</div><div class="number">01 · ORIGEN</div><h3>Independiente</h3><p>Una base construida desde fuentes y componentes elegidos para el proyecto, sin depender de una distribución madre.</p></article>
  <article class="card"><div class="iconbox">⌘</div><div class="number">02 · PAQUETES</div><h3>Nyan</h3><p>Gestor nativo para consultar repositorios, resolver dependencias y administrar paquetes de VANTOR.</p></article>
  <article class="card"><div class="iconbox">⌁</div><div class="number">03 · CONTROL</div><h3>Herramientas propias</h3><p>VANTOR Init, diagnóstico, registros de arranque, recuperación y control de servicios.</p></article>
  <article class="card"><div class="iconbox">◎</div><div class="number">04 · ALCANCE</div><h3>Multigeneración</h3><p>Perfiles separados para hardware x86_64 moderno y equipos x86 de clase i486.</p></article>
 </div>
</div></section>

<section class="section" id="ediciones"><div class="wrap">
 <div class="section-head"><div class="kicker">02 / Ediciones</div><h2>Distintas generaciones. Una misma identidad.</h2><p>Los perfiles se construyen por separado para no prometer compatibilidad universal donde todavía no se ha probado.</p></div>
 <div class="grid three">
  <article class="card edition"><div class="arch">X86_64 · PC</div><h3>VANTOR Minimal</h3><p>El perfil principal: un sistema ligero de consola, BusyBox, Nyan, herramientas de diagnóstico y una ruta hacia un escritorio propio.</p><span class="tag pending">ISO en validación</span></article>
  <article class="card edition"><div class="arch">I486 · LEGACY</div><h3>VANTOR Legacy</h3><p>Perfil separado para equipos antiguos compatibles con i486, con un kernel de la rama 6.1 y un userspace reducido.</p><span class="tag pending">Compatibilidad en pruebas</span></article>
  <article class="card edition"><div class="arch">AARCH64 · ANDROID</div><h3>VANTOR Termux</h3><p>Userspace ARM64 para Android mediante Termux y PRoot-Distro. Android conserva el control del kernel; no es una ISO ni sustituye el arranque de PC.</p><span class="tag">Userspace disponible</span></article>
 </div>
</div></section>

<section class="section" id="arquitectura"><div class="wrap">
 <div class="section-head"><div class="kicker">03 / Arquitectura</div><h2>Componentes claros. Responsabilidades separadas.</h2><p>La arquitectura prioriza un núcleo pequeño, herramientas verificables y componentes que puedan evolucionar sin convertir el sistema base en una colección de dependencias pesadas.</p></div>
 <div class="split">
  <div class="card">
   <h3>La base de VANTOR</h3>
   <ul class="list">
    <li><b>Linux kernel:</b> 6.18.65 para x86_64.</li>
    <li><b>BusyBox:</b> utilidades esenciales y entorno de arranque.</li>
    <li><b>VANTOR Init:</b> inicio, diagnóstico y registro de arranque.</li>
    <li><b>Nyan:</b> paquetes, perfiles y repositorios.</li>
    <li><b>GRUB:</b> menú de arranque con identidad VANTOR.</li>
   </ul>
  </div>
  <div class="card">
   <h3>Control y recuperación</h3>
   <ul class="list">
    <li>Modo recovery mediante parámetro de kernel.</li>
    <li>Diagnóstico con <code>vantorctl doctor</code>.</li>
    <li>Registro de arranque en <code>/var/log/vantor-boot.log</code>.</li>
    <li>Control de servicios y políticas de reinicio.</li>
    <li class="pending">Validación completa en Limbo/QEMU pendiente.</li>
   </ul>
  </div>
 </div>
 <div class="specs" style="margin-top:16px">
  <div class="spec"><b>6.18.65</b><span>Kernel x86_64 fijado</span></div>
  <div class="spec"><b>6.1.193</b><span>Kernel Legacy i486 fijado</span></div>
  <div class="spec"><b>BusyBox</b><span>Userspace mínimo</span></div>
  <div class="spec"><b>Nyan</b><span>Gestor de paquetes nativo</span></div>
 </div>
</div></section>

<section class="section" id="instalar"><div class="wrap">
 <div class="section-head"><div class="kicker">04 / Cómo empezar</div><h2>Prueba el userspace o construye desde el código.</h2><p>El camino depende de dónde quieras probar VANTOR. Los comandos de Termux preparan un entorno de usuario ARM64; no instalan un sistema operativo de arranque dual.</p></div>
 <div class="split">
  <div class="terminal">
   <div class="terminal-top"><span class="dot"></span><span class="dot"></span><span class="dot"></span><span>Android · Termux / ARM64</span></div>
   <pre><code>pkg update
pkg install proot-distro curl coreutils

uname -m
# Debe indicar aarch64

curl -fL "https://raw.githubusercontent.com/Reaccionador2Jeje/vantor-linux/main/tools/termux/install-vantor" -o install-vantor
sh install-vantor

vantor</code></pre>
   <div class="copyhint">Requiere Termux y arquitectura ARM64. Consulta la guía antes de instalar.</div>
  </div>
  <div class="card">
   <h3>Construir desde el repositorio</h3>
   <p>Para desarrolladores que quieran revisar el código, ejecutar pruebas y preparar el entorno de construcción.</p>
   <div class="terminal" style="margin-top:16px">
    <div class="terminal-top">Linux · desarrollo</div>
    <pre><code>git clone https://github.com/Reaccionador2Jeje/vantor-linux.git
cd vantor-linux
make check
make rootfs</code></pre>
   </div>
   <p style="margin-top:14px">El rootfs generado es una etapa del sistema, no una ISO instalada lista para uso diario.</p>
  </div>
 </div>
 <div class="actions"><a class="button primary" href="https://github.com/Reaccionador2Jeje/vantor-linux/releases">Ver versiones y artefactos ↗</a><a class="button secondary" href="https://github.com/Reaccionador2Jeje/vantor-linux/blob/main/docs/termux.md">Guía Termux ↗</a></div>
</div></section>

<section class="section" id="documentacion"><div class="wrap">
 <div class="section-head"><div class="kicker">05 / Documentación</div><h2>Conoce cómo está construido.</h2><p>Documentación técnica y guías mantenidas junto al código fuente.</p></div>
 <div class="grid three docs-grid">
  <article class="card"><div class="number">FUNDAMENTOS</div><h3>Arquitectura</h3><p>Objetivos, límites y organización del sistema.</p><a href="https://github.com/Reaccionador2Jeje/vantor-linux/blob/main/docs/architecture.md">Leer arquitectura <span>↗</span></a></article>
  <article class="card"><div class="number">IDENTIDAD</div><h3>Diseño VANTOR</h3><p>Emblema, paleta, tipografía y reglas visuales.</p><a href="https://github.com/Reaccionador2Jeje/vantor-linux/blob/main/docs/branding.md">Guía de marca <span>↗</span></a></article>
  <article class="card"><div class="number">ARRANQUE</div><h3>Kernel y GRUB</h3><p>Configuración del kernel y sistema de arranque.</p><a href="https://github.com/Reaccionador2Jeje/vantor-linux/blob/main/docs/kernel.md">Documentación kernel <span>↗</span></a></article>
  <article class="card"><div class="number">PAQUETES</div><h3>Nyan</h3><p>Índices, instalación, perfiles y paquetes.</p><a href="https://github.com/Reaccionador2Jeje/vantor-linux/blob/main/docs/nyan.md">Guía Nyan <span>↗</span></a></article>
  <article class="card"><div class="number">INSTALACIÓN</div><h3>Instalador</h3><p>Flujo actual y límites del instalador.</p><a href="https://github.com/Reaccionador2Jeje/vantor-linux/blob/main/docs/installer.md">Guía de instalación <span>↗</span></a></article>
  <article class="card"><div class="number">PRUEBAS</div><h3>Limbo Emulator</h3><p>Plan de pruebas para imágenes y arranque en Android.</p><a href="https://github.com/Reaccionador2Jeje/vantor-linux/blob/main/docs/testing-limbo.md">Guía de pruebas <span>↗</span></a></article>
 </div>
</div></section>

<section class="section"><div class="wrap">
 <div class="mirror">
  <div class="kicker">06 / Nyan Community Mirror</div>
  <h2>Un repositorio abierto de paquetes.</h2>
  <p>Los índices de paquetes se sirven desde GitHub y los archivos se distribuyen mediante GitHub Releases. El espejo no depende de almacenamiento R2.</p>
  <b>Índices disponibles:</b>
  <a class="endpoint" href="/repo/x86_64/Packages">/repo/x86_64/Packages</a>
  <a class="endpoint" href="/repo/aarch64/Packages">/repo/aarch64/Packages</a>
  <p class="muted">El catálogo puede cambiar a medida que se publiquen y validen paquetes.</p>
 </div>
</div></section>
</main>
<footer class="footer"><div class="wrap footer-grid"><div><strong>VANTOR LINUX</strong><br>ONE SYSTEM. EVERY GENERATION.</div><div>Independiente · Abierto · En desarrollo<br><a href="https://github.com/Reaccionador2Jeje/vantor-linux">Código fuente en GitHub ↗</a></div><div>Genesis · Proyecto en evolución</div></div></footer>
<button class="backtop" id="backtop" aria-label="Volver arriba">↑</button>
<script>
const menu=document.getElementById("menu");
const nav=document.getElementById("navlinks");
menu.addEventListener("click",()=>{const open=nav.classList.toggle("open");menu.setAttribute("aria-expanded",String(open));menu.textContent=open?"×":"☰";});
nav.querySelectorAll("a").forEach(link=>link.addEventListener("click",()=>{nav.classList.remove("open");menu.setAttribute("aria-expanded","false");menu.textContent="☰";}));
const topButton=document.getElementById("backtop");
window.addEventListener("scroll",()=>{topButton.style.display=window.scrollY>500?"block":"none";},{passive:true});
topButton.addEventListener("click",()=>window.scrollTo({top:0,behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"}));
</script>
</body>
</html>`;

function json(data, status = 200) {
  return Response.json(data, {
    status,
    headers: { ...SECURITY_HEADERS, "Cache-Control": "no-store" }
  });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method Not Allowed", {
        status: 405,
        headers: { ...SECURITY_HEADERS, Allow: "GET, HEAD" }
      });
    }
    if (url.pathname === "/health") {
      return json({
        ok: true,
        project: "VANTOR Linux",
        phase: "Genesis",
        package_manager: "Nyan",
        mirror: "github-releases",
        website: "full-site"
      });
    }
    const match = url.pathname.match(/^\/repo\/(x86_64|aarch64)\/Packages\/?$/);
    if (match) {
      const upstream = "https://raw.githubusercontent.com/Reaccionador2Jeje/vantor-linux/main/packages/repository/" + match[1] + "/Packages";
      const response = await fetch(upstream, { headers: { Accept: "text/plain" } });
      if (!response.ok) return json({ ok: false, error: "index_unavailable", upstream_status: response.status }, 502);
      return new Response(request.method === "HEAD" ? null : response.body, {
        status: 200,
        headers: { ...SECURITY_HEADERS, "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "public, max-age=60" }
      });
    }
    const pkg = url.pathname.match(/^\/packages\/(x86_64|aarch64)\/([A-Za-z0-9][A-Za-z0-9._+-]*\.tar\.gz)$/);
    if (pkg) {
      const target = "https://github.com/Reaccionador2Jeje/vantor-linux/releases/download/nyan-repository/" + encodeURIComponent(pkg[2]);
      return Response.redirect(target, 302);
    }
    if (url.pathname === "/repo" || url.pathname === "/packages") {
      return json({
        service: "VANTOR Community Mirror",
        package_manager: "Nyan",
        status: "online",
        backend: "GitHub Releases",
        endpoints: { x86_64: "/repo/x86_64/Packages", aarch64: "/repo/aarch64/Packages" }
      });
    }
    if (url.pathname === "/assets/vantor-mark.svg") {
      const svg = await fetch("https://raw.githubusercontent.com/Reaccionador2Jeje/vantor-linux/main/assets/branding/vantor-mark.svg");
      if (!svg.ok) return new Response("Not Found", { status: 404, headers: SECURITY_HEADERS });
      return new Response(svg.body, { headers: { ...SECURITY_HEADERS, "Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=3600" } });
    }
    if (url.pathname !== "/" && url.pathname !== "/index.html") {
      return new Response("Not Found", { status: 404, headers: SECURITY_HEADERS });
    }
    return new Response(request.method === "HEAD" ? null : SITE_HTML, {
      headers: {
        ...SECURITY_HEADERS,
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "public, max-age=300",
        "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
      }
    });
  }
};
