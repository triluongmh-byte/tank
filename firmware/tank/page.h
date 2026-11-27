#pragma once
// Phone control page (Vietnamese). Layout/flow modelled on the crab page (Lái / Wi-Fi / Ráp); code is new.
#ifndef PROGMEM
#define PROGMEM
#endif
namespace tank {
static const char PAGE[] PROGMEM = R"HTML(<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no"><title>Xe Tăng</title>
<style>body{font:18px system-ui,sans-serif;max-width:520px;margin:auto;padding:14px;background:#eef3ee;color:#1d2a1d}h1{font-size:24px;margin:4px 0}button,input,select{font:inherit;min-height:48px;border-radius:10px;padding:8px;border:1px solid #7a8c7a;background:#fff}button:active{background:#b8d9b0}.pad{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.pad button{touch-action:none;user-select:none;-webkit-user-select:none;height:72px}.wide{width:100%;margin:6px 0;box-sizing:border-box}.hidden{display:none}#st{background:#dbe8d6;padding:10px;white-space:pre-line;font-size:16px}#why{color:#a02020;min-height:24px}label{display:block;margin:10px 0}input,select{width:100%;box-sizing:border-box}.row{display:flex;gap:4px;align-items:center;margin:6px 0;flex-wrap:wrap}.row span{flex:1;min-width:90px;font-size:15px}.row button{min-width:44px;padding:4px}#stop{background:#f3b5b5}</style>
<h1>🛡 Xe Tăng</h1><div id="st" role="status">Đang kết nối...</div><div id="why" role="alert"></div>
<nav class="row"><button id="nL">Lái</button><button id="nW">Wi-Fi</button><button id="nR">Ráp</button></nav>
<section id="pL"><div class="pad"><button data-d="5">↖</button><button data-d="1">↑</button><button data-d="6">↗</button><button data-d="3">←</button><button id="stop">DỪNG</button><button data-d="4">→</button><button data-d="7">↙</button><button data-d="2">↓</button><button data-d="8">↘</button></div>
<label>Tốc độ<select id="sp"><option value="0.4">Chậm</option><option value="0.65" selected>Vừa</option><option value="1">Nhanh</option></select></label>
<button id="lt" class="wide">Bật / tắt đèn (chưa nối)</button>
<p>Giữ nút để chạy, thả là dừng. Tới/lui chỉ chạy khi sonar hướng đó còn mới và đủ xa.</p></section>
<section id="pW" class="hidden"><h2>Wi-Fi nhà (tùy chọn)</h2><p>Không bắt buộc: xe vẫn chạy bằng Wi-Fi riêng của xe.</p><button id="sc" class="wide">Tìm Wi-Fi quanh đây</button><label>Chọn mạng<select id="nets"><option value="">Nhấn Tìm Wi-Fi</option></select></label><label>Tên Wi-Fi<input id="ssid" maxlength="32" autocomplete="off"></label><label>Mật khẩu<input id="pw" type="password" maxlength="63" autocomplete="new-password"></label><button id="jn" class="wide">Kết nối</button><div id="wm"></div></section>
<section id="pR" class="hidden"><h2>Ráp và hiệu chuẩn</h2><p>Kê xe cho bánh xoay tự do. Mở trang này khóa lái. Mỗi lần thử chỉ nhích ngắn (khoảng 0,1 s).</p><div id="whl"></div><div class="row"><span id="tc">Turret</span><button data-t="min">Biên −</button><button data-t="center">Giữa</button><button data-t="max">Biên +</button></div><div class="row"><span>Tâm turret</span><button data-tc="-5">−5µs</button><button data-tc="5">+5µs</button></div><button id="sv" class="wide">Lưu hiệu chuẩn</button><button id="dn" class="wide">Xong ráp — về trang Lái</button></section>
<script>
const $=s=>document.querySelector(s);let tok='',seq=0,timer=0,cur=0,asm=false;
async function api(p,b,m){try{const q=new URLSearchParams(b||{}).toString();const g=m==='GET';const r=await fetch(g?p+'?'+q:p,{method:m||'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:g?undefined:q,cache:'no-store'});const j=await r.json().catch(()=>({}));j.code=r.status;return j}catch(e){return{error:'Mất kết nối với xe',code:0}}}
function why(j){$('#why').textContent=j&&j.error?j.error:''}
async function session(){const j=await api('/api/session');if(j.token)tok=j.token;return !!tok}
let busy=false;function send(d,fresh){if(busy&&!fresh)return;busy=true;seq++;return api('/api/move',{token:tok,seq,dir:d,fresh}).then(j=>{busy=false;if(j.error==='Lệnh cũ bị bỏ qua')return;why(j);if(d&&j.code!==200)end()})}
async function begin(d){end();if(!tok&&!await session())return;cur=d;send(d,1);timer=setInterval(()=>send(d,0),150)}
function end(){if(timer){clearInterval(timer);timer=0;if(tok){seq++;api('/api/move',{token:tok,seq,dir:0,fresh:0})}}cur=0}
document.querySelectorAll('[data-d]').forEach(b=>{const d=+b.dataset.d;b.addEventListener('pointerdown',e=>{e.preventDefault();b.setPointerCapture(e.pointerId);begin(d)});['pointerup','pointercancel','lostpointercapture'].forEach(n=>b.addEventListener(n,end))});
$('#stop').onclick=()=>{end();api('/api/stop')};addEventListener('blur',end);document.addEventListener('visibilitychange',()=>{if(document.hidden)end()});
$('#sp').onchange=()=>api('/api/speed',{token:tok,value:$('#sp').value}).then(why);
$('#lt').onclick=()=>api('/api/light',{token:tok}).then(why);
function show(n){['L','W','R'].forEach(k=>$('#p'+k).classList.toggle('hidden',k!==n))}
async function leave(){await api('/api/assembly',{token:tok,active:0});asm=false}
$('#nL').onclick=async()=>{end();if(asm)await leave();show('L')};$('#nW').onclick=async()=>{end();if(asm)await leave();show('W')};
$('#nR').onclick=async()=>{end();if(!tok)await session();const j=await api('/api/assembly',{token:tok,active:1});why(j);if(j.ok){asm=true;show('R');cal()}};
$('#dn').onclick=async()=>{await leave();show('L')};
async function cal(){const j=await api('/api/cal',{},'GET');if(!j.neutral)return;$('#tc').textContent='Turret tâm '+j.turretCenter+'µs, biên '+j.yawMin+'..'+j.yawMax+'°';let h='';for(let i=0;i<6;i++){h+=`<div class="row"><span>Bánh ${i+1}<br>tâm ${j.neutral[i]} biên ${j.span[i]} ${j.direction[i]>0?'thuận':'ngược'}${j.calibrated[i]?' ✔':' (chưa)'}</span><button data-c="${i}:n:-5">tâm−</button><button data-c="${i}:n:5">tâm+</button><button data-c="${i}:d:0">đảo</button><button data-c="${i}:s:-10">−biên</button><button data-c="${i}:s:10">+biên</button><button data-j="${i}:-1">⟲</button><button data-j="${i}:0">0</button><button data-j="${i}:1">⟳</button></div>`}$('#whl').innerHTML=h}
$('#pR').addEventListener('click',async e=>{const b=e.target.closest('button');if(!b)return;let j;if(b.dataset.c){const[ch,k,dl]=b.dataset.c.split(':');j=await api('/api/trim',{token:tok,ch,kind:k,delta:dl});cal()}else if(b.dataset.j){const[ch,d]=b.dataset.j.split(':');j=await api('/api/jog',{token:tok,ch,d})}else if(b.dataset.t)j=await api('/api/turret',{token:tok,pos:b.dataset.t});else if(b.dataset.tc){j=await api('/api/turretcal',{token:tok,delta:b.dataset.tc});cal()}else if(b.id==='sv')j=await api('/api/save',{token:tok});why(j)});
$('#sc').onclick=async()=>{$('#wm').textContent='Đang tìm...';for(let i=0;i<8;i++){const j=await api('/api/scan',{});if(j.networks){$('#nets').innerHTML='<option value="">Chọn</option>'+j.networks.map(n=>'<option>'+n.replace(/[<>&"]/g,'')+'</option>').join('');$('#wm').textContent='Xong.';return}await new Promise(r=>setTimeout(r,1000))}$('#wm').textContent='Không tìm thấy mạng nào.'};
$('#nets').onchange=()=>{$('#ssid').value=$('#nets').value};
$('#jn').onclick=async()=>{const j=await api('/api/wifi',{ssid:$('#ssid').value,password:$('#pw').value});$('#wm').textContent=j.error||'Đang kết nối (tối đa 18 giây)...';$('#pw').value=''};
async function poll(){const j=await api('/api/status',{token:tok},'GET');if(j.text){$('#st').textContent=j.text;if(j.owner===false&&!asm)tok='';if(j.block&&cur)$('#why').textContent=j.block}else{$('#st').textContent='Mất kết nối với xe. Đang thử lại...';if(!tok)session()}setTimeout(poll,1000)}
session().then(poll);
</script></html>)HTML";
}
