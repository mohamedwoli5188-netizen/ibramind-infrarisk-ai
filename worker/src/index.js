const SYSTEM_PROMPT = `You are IBRAMIND InfraRisk AI, an infrastructure project risk analyst.
Use only the supplied project context and evidence. Do not invent facts.
Every finding must cite one or more evidence IDs that exist in the input.
Return valid JSON only, with a top-level key "findings". Each finding must contain:
risk, severity (low|medium|high|critical), confidence (0..1), evidence_ids,
rationale, recommended_action.
Prioritize schedule, cost, quality, safety, contractual, and constructability risks.
If evidence is insufficient, say so explicitly and lower confidence.`;

const EXAMPLE = {
  project_name: "Synthetic Bridge Rehabilitation Package",
  project_context: "A rehabilitation package with constrained access, a short-term programme, and QA hold points. All evidence is synthetic for demonstration.",
  evidence: [
    { id: "E-001", type: "site_diary", text: "Scaffolding access to Pier 2 is delayed by four days because the access platform has not been released." },
    { id: "E-002", type: "programme", text: "Pier 2 concrete repair has three days total float and precedes bearing replacement on the current critical path sequence." },
    { id: "E-003", type: "qa_qc", text: "Surface-preparation inspection failed at Pier 2; reinspection is required before repair mortar placement can start." }
  ]
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }
  });
}

function validatePayload(body) {
  if (!body || typeof body !== "object") return "Request body must be JSON.";
  if (!body.project_name || !body.project_context) return "project_name and project_context are required.";
  if (!Array.isArray(body.evidence) || body.evidence.length === 0) return "At least one evidence item is required.";
  const ids = new Set();
  for (const item of body.evidence) {
    if (!item?.id || !item?.type || !item?.text) return "Each evidence item requires id, type, and text.";
    if (ids.has(item.id)) return `Duplicate evidence id: ${item.id}`;
    ids.add(item.id);
  }
  return null;
}

function sanitizeFindings(findings, allowedIds) {
  if (!Array.isArray(findings)) return [];
  return findings.map((f) => ({
    risk: String(f?.risk || "Unspecified risk"),
    severity: ["low", "medium", "high", "critical"].includes(String(f?.severity || "").toLowerCase()) ? String(f.severity).toLowerCase() : "medium",
    confidence: Math.max(0, Math.min(1, Number(f?.confidence ?? 0))),
    evidence_ids: Array.isArray(f?.evidence_ids) ? f.evidence_ids.filter((id) => allowedIds.has(id)) : [],
    rationale: String(f?.rationale || ""),
    recommended_action: String(f?.recommended_action || "")
  }));
}

async function analyze(request, env) {
  if (!env.NEBIUS_API_KEY) return json({ error: "Demo runtime is not configured yet." }, 503);
  const body = await request.json().catch(() => null);
  const validationError = validatePayload(body);
  if (validationError) return json({ error: validationError }, 400);
  const model = env.NVIDIA_MODEL;
  if (!model) return json({ error: "NVIDIA model is not configured yet." }, 503);

  const started = Date.now();
  const res = await fetch(`${env.NEBIUS_BASE_URL || "https://api.tokenfactory.nebius.com/v1"}/chat/completions`, {
    method: "POST",
    headers: {
      "authorization": `Bearer ${env.NEBIUS_API_KEY}`,
      "content-type": "application/json"
    },
    body: JSON.stringify({
      model,
      temperature: 0.1,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: JSON.stringify(body) }
      ]
    })
  });

  const raw = await res.text();
  if (!res.ok) return json({ error: "Nebius inference failed", status: res.status, detail: raw.slice(0, 1200) }, 502);
  let upstream;
  try { upstream = JSON.parse(raw); } catch { return json({ error: "Nebius returned non-JSON response." }, 502); }
  const content = upstream?.choices?.[0]?.message?.content || "{}";
  let parsed;
  try { parsed = JSON.parse(content); } catch { return json({ error: "Model returned invalid structured output.", raw: content.slice(0, 1200) }, 502); }

  const allowedIds = new Set(body.evidence.map((e) => e.id));
  const findings = sanitizeFindings(parsed.findings, allowedIds);
  const cited = new Set(findings.flatMap((f) => f.evidence_ids));
  return json({
    project_name: body.project_name,
    findings,
    runtime: {
      provider: "Nebius Token Factory",
      model,
      latency_ms: Date.now() - started,
      evidence_items: body.evidence.length,
      cited_evidence_items: cited.size,
      evidence_coverage: body.evidence.length ? Number((cited.size / body.evidence.length).toFixed(2)) : 0,
      usage: upstream?.usage || null
    }
  });
}

const HTML = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IBRAMIND InfraRisk AI</title><style>
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#13211a;background:#f4f5ef}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top right,#dcece2,transparent 34%),#f4f5ef}.wrap{max-width:1120px;margin:auto;padding:28px}.hero{background:#111a16;color:#f8f5e9;border-radius:26px;padding:32px;box-shadow:0 16px 48px #14251b1a}.eyebrow{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#80d8a0}.hero h1{font-size:clamp(34px,6vw,64px);line-height:.98;margin:14px 0}.hero p{max-width:760px;color:#cbd7cf;font-size:17px;line-height:1.55}.badges{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px}.badge{border:1px solid #ffffff26;border-radius:999px;padding:7px 11px;font-size:12px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px}.card{background:#fff;border:1px solid #dde3dc;border-radius:20px;padding:20px;box-shadow:0 8px 30px #1a2f2010}h2{margin:0 0 12px;font-size:20px}label{display:block;font-size:12px;font-weight:700;margin:14px 0 6px;color:#48534c}input,textarea{width:100%;border:1px solid #ccd5cd;background:#fbfcfa;border-radius:12px;padding:11px 12px;font:inherit}textarea{min-height:78px;resize:vertical}.evidence{border-top:1px solid #e6ebe5;margin-top:12px;padding-top:12px}.row{display:grid;grid-template-columns:100px 140px 1fr;gap:8px}.actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:16px}button{border:0;border-radius:12px;padding:11px 15px;font-weight:800;cursor:pointer}button.primary{background:#0a6c3b;color:white}button.secondary{background:#ecf2ed;color:#21412e}.status{font-size:13px;margin-top:10px;color:#58655d}.finding{border:1px solid #dde6df;border-radius:16px;padding:15px;margin:10px 0}.top{display:flex;justify-content:space-between;gap:10px}.sev{text-transform:uppercase;font-size:11px;font-weight:900;letter-spacing:.08em}.sev.critical,.sev.high{color:#9e2d22}.sev.medium{color:#956517}.sev.low{color:#22714a}.cite{display:inline-block;background:#eef4ef;border-radius:7px;padding:3px 7px;margin:2px;font-size:11px}.metricbar{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:12px 0}.metric{background:#f2f6f3;border-radius:11px;padding:10px}.metric b{display:block;font-size:16px}.metric span{font-size:10px;color:#68766e}.empty{color:#6d786f;padding:28px 0;text-align:center}.foot{font-size:12px;color:#667269;margin:18px 3px}.spin{display:inline-block;width:13px;height:13px;border:2px solid #a5beb0;border-top-color:#0a6c3b;border-radius:50%;animation:s .8s linear infinite}@keyframes s{to{transform:rotate(360deg)}}@media(max-width:800px){.grid{grid-template-columns:1fr}.row{grid-template-columns:1fr}.metricbar{grid-template-columns:1fr 1fr}}
</style></head><body><main class="wrap"><section class="hero"><div class="eyebrow">IBRAMIND Engineering Intelligence · Hackathon Build</div><h1>InfraRisk AI</h1><p>Evidence-grounded infrastructure risk intelligence. Connect site records, programme constraints and QA evidence to auditable risks — with exact evidence citations, confidence and recommended actions.</p><div class="badges"><span class="badge">Nebius Token Factory</span><span class="badge">NVIDIA Nemotron</span><span class="badge">Evidence-grounded</span><span class="badge">Synthetic demo data</span></div></section><section class="grid"><div class="card"><h2>Engineering evidence</h2><label>Project</label><input id="project"><label>Context</label><textarea id="context"></textarea><div id="evidence"></div><div class="actions"><button class="secondary" id="load">Load synthetic example</button><button class="primary" id="run">Analyze risk →</button></div><div id="status" class="status">No production/customer data is used in this demo.</div></div><div class="card"><h2>Auditable risk findings</h2><div id="metrics"></div><div id="results" class="empty">Run the analysis to see evidence-linked findings.</div></div></section><div class="foot">Hackathon-specific open-source prototype. Human review remains required for engineering decisions.</div></main><script>
let items=[]; const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
function draw(){document.getElementById('evidence').innerHTML=items.map((e,i)=>'<div class="evidence"><div class="row"><input data-i="'+i+'" data-k="id" value="'+esc(e.id)+'"><input data-i="'+i+'" data-k="type" value="'+esc(e.type)+'"><textarea data-i="'+i+'" data-k="text">'+esc(e.text)+'</textarea></div></div>').join('');document.querySelectorAll('[data-i]').forEach(el=>el.oninput=()=>items[+el.dataset.i][el.dataset.k]=el.value)}
function load(){project.value=${JSON.stringify(EXAMPLE.project_name)};context.value=${JSON.stringify(EXAMPLE.project_context)};items=${JSON.stringify(EXAMPLE.evidence)};draw()} load();
load.onclick=load;run.onclick=async()=>{run.disabled=true;status.innerHTML='<span class="spin"></span> Running live analysis on Nebius…';results.className='empty';results.textContent='Waiting for model output…';metrics.innerHTML='';try{const r=await fetch('/api/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({project_name:project.value,project_context:context.value,evidence:items})});const d=await r.json();if(!r.ok)throw new Error(d.detail||d.error||'Analysis failed');const rt=d.runtime||{};metrics.innerHTML='<div class="metricbar"><div class="metric"><b>'+esc(rt.latency_ms)+' ms</b><span>LIVE LATENCY</span></div><div class="metric"><b>'+esc(d.findings.length)+'</b><span>RISKS FOUND</span></div><div class="metric"><b>'+esc(Math.round((rt.evidence_coverage||0)*100))+'%</b><span>EVIDENCE COVERAGE</span></div><div class="metric"><b>'+esc(rt.model||'—')+'</b><span>MODEL</span></div></div>';results.className='';results.innerHTML=d.findings.map(f=>'<article class="finding"><div class="top"><strong>'+esc(f.risk)+'</strong><span class="sev '+esc(f.severity)+'">'+esc(f.severity)+' · '+Math.round(f.confidence*100)+'%</span></div><p>'+esc(f.rationale)+'</p><div>'+f.evidence_ids.map(id=>'<span class="cite">'+esc(id)+'</span>').join('')+'</div><p><b>Action:</b> '+esc(f.recommended_action)+'</p></article>').join('')||'<div class="empty">No supported risk findings returned.</div>';status.textContent='Live Nebius inference completed.'}catch(e){results.className='empty';results.textContent=e.message;status.textContent='Runtime error — see result panel.'}finally{run.disabled=false}};
</script></body></html>`;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/") return new Response(HTML, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
    if (request.method === "GET" && url.pathname === "/health") return json({ status: "ok", provider: "Nebius Token Factory", configured: Boolean(env.NEBIUS_API_KEY && env.NVIDIA_MODEL), model: env.NVIDIA_MODEL || null });
    if (request.method === "POST" && url.pathname === "/api/analyze") return analyze(request, env);
    return new Response("Not found", { status: 404 });
  }
};
