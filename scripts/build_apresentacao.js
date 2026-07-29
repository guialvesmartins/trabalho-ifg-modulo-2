const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const {
  FaRocket, FaDatabase, FaCogs, FaBrain, FaChartBar, FaCloud,
  FaCheckCircle, FaImage, FaFileAlt, FaArrowRight,
  FaStar, FaShoppingCart, FaDocker
} = require("react-icons/fa");

async function renderIcon(Icon, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(Icon, { color, size: String(size) })
  );
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "IFG - Pos IA Aplicada";
  pres.title = "Previsao de Satisfacao em E-commerce";

  const C = {
    bg: "0F172A",
    card: "1E293B",
    accent: "0891B2",
    white: "F8FAFC",
    muted: "94A3B8",
    warn: "EA580C",
    green: "10B981",
    star: "EAB308",
  };

  const icons = {};
  for (const [name, Icon] of [
    ["db", FaDatabase], ["gear", FaCogs], ["brain", FaBrain],
    ["chart", FaChartBar], ["cloud", FaCloud], ["check", FaCheckCircle],
    ["image", FaImage], ["doc", FaFileAlt], ["arrow", FaArrowRight],
    ["star", FaStar], ["cart", FaShoppingCart], ["docker", FaDocker],
    ["rocket", FaRocket]
  ]) {
    icons[name] = await renderIcon(Icon, `#${C.accent}`);
    icons[`${name}W`] = await renderIcon(Icon, `#${C.white}`);
  }

  function addIcon(slide, name, x, y, w, h) {
    if (icons[name]) slide.addImage({ data: icons[name], x, y, w, h });
  }

  function card(slide, x, y, w, h, accentLeft = false) {
    slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: C.card }, shadow: { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.2, angle: 135 } });
    if (accentLeft) {
      slide.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.07, h, fill: { color: C.accent } });
    }
  }

  function titleBar(slide, num, text) {
    slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent } });
    slide.addText(`${String(num).padStart(2,"0")}`, { x: 0.5, y: 0.3, w: 0.6, h: 0.5, fontSize: 14, color: C.accent, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    slide.addText(text, { x: 1.1, y: 0.25, w: 8.4, h: 0.6, fontSize: 28, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.85, w: 1.2, h: 0.04, fill: { color: C.accent } });
  }

  // ================================================================
  // SLIDE 1 - CAPA
  // ================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.bg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.08, fill: { color: C.accent } });
    addIcon(s, "cartW", 0.7, 1.0, 0.8, 0.8);
    s.addText("PREVISÃO DE SATISFAÇÃO", { x: 0.7, y: 1.3, w: 8.6, h: 0.5, fontSize: 14, color: C.accent, fontFace: "Calibri", bold: true, charSpacing: 6, margin: 0 });
    s.addText("em E-commerce com\nDados Multimodais", { x: 0.7, y: 2.05, w: 8.6, h: 1.4, fontSize: 38, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    s.addText("Texto + Imagens + Dados Estruturados", { x: 0.7, y: 3.7, w: 8.6, h: 0.4, fontSize: 16, color: C.muted, fontFace: "Calibri", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 4.35, w: 2.5, h: 0.04, fill: { color: C.accent } });
    s.addText("IFG · Pós-Graduação em Inteligência Artificial Aplicada · Módulo 2", { x: 0.7, y: 4.6, w: 8.6, h: 0.35, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
  }

  // ================================================================
  // SLIDE 2 - O PROBLEMA
  // ================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.bg };
    titleBar(s, 1, "O Problema");

    card(s, 0.5, 1.2, 4.2, 1.7, true);
    addIcon(s, "cart", 0.8, 1.4, 0.45, 0.45);
    s.addText("Contexto", { x: 1.45, y: 1.35, w: 3, h: 0.4, fontSize: 16, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    s.addText("Um marketplace recebe milhares de\nprodutos. O gerente precisa decidir\nquais precisam de intervenção antes\nque as vendas caiam.", { x: 0.8, y: 1.85, w: 3.7, h: 0.9, fontSize: 12, color: C.muted, fontFace: "Calibri", margin: 0 });

    card(s, 5.3, 1.2, 4.2, 1.7, true);
    addIcon(s, "star", 5.6, 1.4, 0.45, 0.45);
    s.addText("Solução", { x: 6.25, y: 1.35, w: 3, h: 0.4, fontSize: 16, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    s.addText("Sistema de IA que prevê a nota\n(1 a 5 estrelas) que um produto\nreceberá, analisando o anúncio\nantes mesmo de ser publicado.", { x: 5.6, y: 1.85, w: 3.7, h: 0.9, fontSize: 12, color: C.muted, fontFace: "Calibri", margin: 0 });

    card(s, 0.5, 3.2, 9, 1.8);
    s.addText("Como funciona", { x: 0.8, y: 3.35, w: 8, h: 0.4, fontSize: 16, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    const flow = [
      { text: "Preço + Categoria  ", options: { fontSize: 14, color: C.white, fontFace: "Calibri", bold: true } },
      { text: "+  ", options: { fontSize: 14, color: C.accent, fontFace: "Calibri", bold: true } },
      { text: "Texto da Review  ", options: { fontSize: 14, color: C.white, fontFace: "Calibri", bold: true } },
      { text: "+  ", options: { fontSize: 14, color: C.accent, fontFace: "Calibri", bold: true } },
      { text: "Foto do Produto  ", options: { fontSize: 14, color: C.white, fontFace: "Calibri", bold: true } },
      { text: "→  ", options: { fontSize: 14, color: C.green, fontFace: "Calibri", bold: true } },
      { text: "IA prevê:  ", options: { fontSize: 14, color: C.white, fontFace: "Calibri", bold: true } },
      { text: "1⭐   2⭐   3⭐   4⭐   5⭐", options: { fontSize: 14, color: C.star, fontFace: "Calibri", bold: true } },
    ];
    s.addText(flow, { x: 0.8, y: 3.85, w: 8.4, h: 0.5, margin: 0 });
    s.addText("O gerente age ANTES do problema — ajusta preço, melhora a foto, revisa a descrição.", { x: 0.8, y: 4.45, w: 8.4, h: 0.4, fontSize: 12, color: C.muted, fontFace: "Calibri", margin: 0 });
  }

  // ================================================================
  // SLIDE 3 - OS DADOS
  // ================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.bg };
    titleBar(s, 2, "Os Dados");

    const cols = [
      { icon: "doc", title: "Estruturados", desc: "Preço, desconto, categoria,\navaliações anteriores.\n~10 features numéricas." },
      { icon: "doc", title: "Texto (NLP)", desc: "Título e conteúdo da review.\nSentimento, palavras-chave.\n~50 features textuais." },
      { icon: "image", title: "Imagem (CV)", desc: "Foto do produto.\nNitidez, brilho, cores.\n~6 features visuais." },
    ];

    cols.forEach((col, i) => {
      const cx = 0.5 + i * 3.1;
      card(s, cx, 1.2, 2.9, 2.2, true);
      addIcon(s, col.icon, cx + 0.3, 1.4, 0.4, 0.4);
      s.addText(col.title, { x: cx + 0.85, y: 1.4, w: 1.8, h: 0.4, fontSize: 15, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
      s.addText(col.desc, { x: cx + 0.3, y: 2.0, w: 2.3, h: 1.2, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
    });

    card(s, 0.5, 3.7, 9, 1.6);
    s.addText("Dataset: Amazon Sales (Kaggle)", { x: 0.8, y: 3.85, w: 8, h: 0.35, fontSize: 15, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    const stats = [
      { val: "1.351", label: "Produtos" },
      { val: "1.194", label: "Reviews" },
      { val: "500", label: "Fotos\nprocessadas" },
      { val: "87", label: "Features\nno modelo" },
    ];
    stats.forEach((st, i) => {
      const sx = 0.8 + i * 2.2;
      s.addText(st.val, { x: sx, y: 4.3, w: 1.8, h: 0.5, fontSize: 28, color: C.accent, fontFace: "Trebuchet MS", bold: true, align: "center", margin: 0 });
      s.addText(st.label, { x: sx, y: 4.8, w: 1.8, h: 0.35, fontSize: 10, color: C.muted, fontFace: "Calibri", align: "center", margin: 0 });
    });
  }

  // ================================================================
  // SLIDE 4 - ARQUITETURA
  // ================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.bg };
    titleBar(s, 3, "Arquitetura");

    const boxes = [
      { label: "MinIO", desc: "Armazenamento\n(S3 mock)", x: 0.4, y: 1.3, color: "0D9488" },
      { label: "PostgreSQL", desc: "Banco de dados\n(Snowflake mock)", x: 2.6, y: 1.3, color: "2563EB" },
      { label: "Airflow", desc: "Orquestrador\n(DAG 8 etapas)", x: 4.8, y: 1.3, color: "EA580C" },
      { label: "Metabase", desc: "Dashboard\n(4 painéis)", x: 7.0, y: 1.3, color: "8B5CF6" },
    ];

    boxes.forEach(b => {
      s.addShape(pres.shapes.RECTANGLE, { x: b.x, y: b.y, w: 2.0, h: 1.5, fill: { color: "1E293B" }, shadow: { type: "outer", blur: 4, offset: 1, color: "000000", opacity: 0.2, angle: 135 } });
      s.addShape(pres.shapes.RECTANGLE, { x: b.x, y: b.y, w: 2.0, h: 0.06, fill: { color: b.color } });
      s.addText(b.label, { x: b.x, y: b.y + 0.2, w: 2.0, h: 0.45, fontSize: 16, color: C.white, fontFace: "Trebuchet MS", bold: true, align: "center", margin: 0 });
      s.addText(b.desc, { x: b.x + 0.1, y: b.y + 0.65, w: 1.8, h: 0.7, fontSize: 10, color: C.muted, fontFace: "Calibri", align: "center", margin: 0 });
    });

    card(s, 0.5, 3.1, 9, 1.2);
    s.addText("Python Scripts (ingestão, NLP, CV, ML)", { x: 0.8, y: 3.2, w: 8, h: 0.35, fontSize: 14, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    s.addText("dbt-core: staging → dimensões → fatos → tabela ML pronta", { x: 0.8, y: 3.6, w: 8, h: 0.3, fontSize: 12, color: C.muted, fontFace: "Calibri", margin: 0 });
    s.addText("Tudo sobe com: docker compose up", { x: 0.8, y: 4.0, w: 8, h: 0.3, fontSize: 12, color: C.green, fontFace: "Calibri", bold: true, margin: 0 });

    card(s, 0.5, 4.6, 9, 0.7);
    s.addText("Troca DEV → PROD:  4 variáveis no .env   |   MinIO → AWS S3   |   PostgreSQL → Snowflake", { x: 0.8, y: 4.68, w: 8.4, h: 0.6, fontSize: 12, color: C.accent, fontFace: "Calibri", bold: true, align: "center", margin: 0 });
  }

  // ================================================================
  // SLIDE 5 - PIPELINE
  // ================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.bg };
    titleBar(s, 4, "Pipeline ELT (8 Etapas)");

    const steps = [
      { n: "1", label: "Download" },
      { n: "2", label: "Upload S3" },
      { n: "3", label: "Limpeza" },
      { n: "4a", label: "NLP", sub: true },
      { n: "4b", label: "CV", sub: true },
      { n: "5", label: "Merge" },
      { n: "6", label: "dbt" },
      { n: "8", label: "ML" },
    ];

    const startX = 0.55;
    const boxW = 0.85;
    const gap = 0.25;
    let cx = startX;

    steps.forEach((st, i) => {
      const yOff = st.sub ? 0.0 : 0.0;
      const mainY = st.sub ? 1.3 : 1.8;
      const isParallel = st.n === "4a" || st.n === "4b";
      const bgColor = isParallel ? "0D9488" : C.accent;

      s.addShape(pres.shapes.RECTANGLE, { x: cx, y: mainY + yOff, w: boxW, h: 0.85, fill: { color: "1E293B" }, shadow: { type: "outer", blur: 3, offset: 1, color: "000000", opacity: 0.15, angle: 135 } });
      s.addShape(pres.shapes.RECTANGLE, { x: cx, y: mainY + yOff, w: boxW, h: 0.05, fill: { color: bgColor } });
      s.addText(st.n, { x: cx, y: mainY + 0.05 + yOff, w: boxW, h: 0.35, fontSize: 16, color: bgColor, fontFace: "Trebuchet MS", bold: true, align: "center", margin: 0 });
      s.addText(st.label, { x: cx, y: mainY + 0.4 + yOff, w: boxW, h: 0.4, fontSize: 8, color: C.muted, fontFace: "Calibri", align: "center", margin: 0 });

      if (i < steps.length - 1 && !isParallel) {
        const arrowX = cx + boxW;
        const arrowY = mainY + 0.32 + yOff;
        s.addText("→", { x: arrowX, y: arrowY, w: gap, h: 0.2, fontSize: 12, color: C.accent, align: "center", margin: 0 });
      }

      cx += boxW + gap;
    });

    // Highlight background for parallel steps
    s.addShape(pres.shapes.RECTANGLE, { x: startX + 3 * (boxW + gap) - 0.05, y: 1.25, w: 2 * (boxW + gap) - 0.1, h: 0.95, fill: { color: "0D9488", transparency: 85 } });

    card(s, 0.5, 2.8, 9, 0.65);
    s.addText("⚡ NLP e CV rodam em paralelo (independência entre texto e imagem)", { x: 0.8, y: 2.85, w: 8.4, h: 0.55, fontSize: 12, color: C.green, fontFace: "Calibri", margin: 0 });

    card(s, 0.5, 3.7, 9, 1.0);
    s.addText("Orquestração — Apache Airflow", { x: 0.8, y: 3.78, w: 8, h: 0.35, fontSize: 14, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    s.addText("DAG (Directed Acyclic Graph): arquivo Python que define o que roda, em qual ordem\ne com quais dependências. Agenda diária ou execução manual.", { x: 0.8, y: 4.18, w: 8.4, h: 0.45, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
  }

  // ================================================================
  // SLIDE 6 - NLP & CV
  // ================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.bg };
    titleBar(s, 5, "NLP & Visão Computacional");

    card(s, 0.5, 1.2, 4.2, 2.4, true);
    addIcon(s, "doc", 0.8, 1.4, 0.4, 0.4);
    s.addText("NLP — Análise de Texto", { x: 1.4, y: 1.35, w: 3.0, h: 0.4, fontSize: 15, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    const nlpItems = [
      { text: "VADER: sentimento do texto (-1 a +1)\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "TF-IDF: palavras mais importantes\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Regex: detecta reclamação, elogio,\n  menção a preço e entrega", options: { bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
    ];
    s.addText(nlpItems, { x: 0.8, y: 1.9, w: 3.7, h: 1.5, margin: 0 });

    card(s, 5.3, 1.2, 4.2, 2.4, true);
    addIcon(s, "image", 5.6, 1.4, 0.4, 0.4);
    s.addText("CV — Análise de Imagem", { x: 6.2, y: 1.35, w: 3.0, h: 0.4, fontSize: 15, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    const cvItems = [
      { text: "OpenCV: nitidez, brilho, saturação\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Canny Edge: densidade de bordas\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Hipótese: fotos escuras ou borradas\n  estão ligadas a ratings piores?", options: { bullet: true, fontSize: 11, color: C.warn, fontFace: "Calibri" } },
    ];
    s.addText(cvItems, { x: 5.6, y: 1.9, w: 3.7, h: 1.5, margin: 0 });

    card(s, 0.5, 3.9, 9, 1.4);
    s.addText("500 fotos de produtos processadas com OpenCV", { x: 0.8, y: 4.0, w: 8, h: 0.3, fontSize: 13, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    const imgStats = [
      { val: "300x300", label: "Tamanho\nmédio" },
      { val: "158.6", label: "Brilho\nmédio" },
      { val: "1.234", label: "Blur score\nmédio" },
    ];
    imgStats.forEach((st, i) => {
      const sx = 0.8 + i * 3;
      s.addText(st.val, { x: sx, y: 4.4, w: 2.5, h: 0.4, fontSize: 22, color: C.accent, fontFace: "Trebuchet MS", bold: true, align: "center", margin: 0 });
      s.addText(st.label, { x: sx, y: 4.8, w: 2.5, h: 0.35, fontSize: 10, color: C.muted, fontFace: "Calibri", align: "center", margin: 0 });
    });
  }

  // ================================================================
  // SLIDE 7 - MACHINE LEARNING
  // ================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.bg };
    titleBar(s, 6, "Machine Learning");

    card(s, 0.5, 1.2, 4.2, 2.2, true);
    addIcon(s, "brain", 0.8, 1.4, 0.4, 0.4);
    s.addText("Naive Bayes", { x: 1.4, y: 1.35, w: 3.0, h: 0.4, fontSize: 16, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    s.addText("Classificação multiclasse\nPrevê rating de 1 a 5 estrelas\nbaseado em ~87 features\ncombinando texto + imagem + preço.", { x: 0.8, y: 1.85, w: 3.7, h: 1.3, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });

    card(s, 5.3, 1.2, 4.2, 2.2, true);
    addIcon(s, "gear", 5.6, 1.4, 0.4, 0.4);
    s.addText("Dupla implementação", { x: 6.2, y: 1.35, w: 3.0, h: 0.4, fontSize: 16, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    const impl = [
      { text: "Hard-code: algoritmo do zero\n  (Python puro + NumPy)\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Sklearn: MultinomialNB\n  (biblioteca scikit-learn)", options: { bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
    ];
    s.addText(impl, { x: 5.6, y: 1.85, w: 3.7, h: 1.3, margin: 0 });

    card(s, 0.5, 3.7, 9, 1.6);
    s.addText("Comparação & Métricas", { x: 0.8, y: 3.8, w: 8, h: 0.35, fontSize: 15, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    const metricas = ["Acurácia", "Precisão", "Recall", "F1-Score", "Matriz de Confusão", "Tempo de Treino"];
    metricas.forEach((m, i) => {
      const mx = 0.8 + (i % 3) * 3;
      const my = 4.25 + Math.floor(i / 3) * 0.5;
      s.addShape(pres.shapes.RECTANGLE, { x: mx, y: my, w: 2.5, h: 0.4, fill: { color: "1E293B" } });
      s.addShape(pres.shapes.RECTANGLE, { x: mx, y: my, w: 0.06, h: 0.4, fill: { color: C.accent } });
      s.addText(m, { x: mx + 0.15, y: my, w: 2.3, h: 0.4, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
    });
  }

  // ================================================================
  // SLIDE 8 - DASHBOARD
  // ================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.bg };
    titleBar(s, 7, "Dashboard — Metabase");

    card(s, 0.5, 1.2, 5.5, 4.0, true);
    s.addText("Resumo Executivo", { x: 0.8, y: 1.35, w: 5, h: 0.4, fontSize: 16, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    const kpis = [
      { text: "3 KPIs no topo: total de produtos,\n  rating médio, % reviews negativas\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Gráfico: rating por categoria\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Gráfico: polaridade (sentimento)\n  do texto vs rating\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Tabela: top 10 piores produtos\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Palavras mais relevantes\n  para reviews nota 5", options: { bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
    ];
    s.addText(kpis, { x: 0.8, y: 1.9, w: 5, h: 3.0, margin: 0 });

    card(s, 6.5, 1.2, 3.0, 4.0);
    s.addText("Configuração\nautomática", { x: 6.8, y: 1.5, w: 2.5, h: 0.8, fontSize: 15, color: C.white, fontFace: "Trebuchet MS", bold: true, align: "center", margin: 0 });
    const autoItems = [
      { text: "Conexão com banco\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "10 perguntas SQL\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Painel montado\nem 1 comando", options: { bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
    ];
    s.addText(autoItems, { x: 6.8, y: 2.5, w: 2.5, h: 2.0, margin: 0 });
    s.addText("make up", { x: 6.8, y: 4.6, w: 2.5, h: 0.4, fontSize: 14, color: C.green, fontFace: "Consolas", bold: true, align: "center", margin: 0 });
  }

  // ================================================================
  // SLIDE 9 - AWS / NUVEM
  // ================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.bg };
    titleBar(s, 8, "Nuvem — AWS & Snowflake");

    card(s, 0.5, 1.2, 4.2, 2.5, true);
    addIcon(s, "cloud", 0.8, 1.4, 0.4, 0.4);
    s.addText("CloudFormation (YAML)", { x: 1.4, y: 1.35, w: 3, h: 0.4, fontSize: 15, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    const awsItems = [
      { text: "S3: armazenamento de dados\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "EC2: servidor do Airflow\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "ECS: containers dbt + scripts\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "SageMaker: treino do modelo\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Redshift: data warehouse", options: { bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
    ];
    s.addText(awsItems, { x: 0.8, y: 1.9, w: 3.7, h: 1.6, margin: 0 });

    card(s, 5.3, 1.2, 4.2, 2.5, true);
    s.addText("Dev  →  Prod", { x: 5.6, y: 1.35, w: 3.7, h: 0.45, fontSize: 16, color: C.white, fontFace: "Trebuchet MS", bold: true, align: "center", margin: 0 });
    s.addText("4 variáveis no .env", { x: 5.6, y: 1.8, w: 3.7, h: 0.3, fontSize: 12, color: C.accent, fontFace: "Calibri", align: "center", margin: 0 });

    const envRows = [
      ["MinIO (local)", "→", "AWS S3"],
      ["PostgreSQL", "→", "Snowflake"],
      ["Airflow local", "→", "EC2"],
      ["Metabase local", "→", "QuickSight"],
    ];
    envRows.forEach((row, i) => {
      const ry = 2.3 + i * 0.33;
      s.addText(row[0], { x: 5.7, y: ry, w: 1.5, h: 0.3, fontSize: 10, color: C.muted, fontFace: "Calibri", align: "right", margin: 0 });
      s.addText(row[1], { x: 7.2, y: ry, w: 0.4, h: 0.3, fontSize: 10, color: C.accent, fontFace: "Calibri", align: "center", margin: 0 });
      s.addText(row[2], { x: 7.6, y: ry, w: 1.5, h: 0.3, fontSize: 10, color: C.green, fontFace: "Calibri", align: "left", margin: 0 });
    });

    card(s, 0.5, 4.0, 9, 1.3);
    s.addText("Nenhum código muda. Só o destino dos dados.", { x: 0.8, y: 4.1, w: 8.4, h: 0.35, fontSize: 15, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    s.addText("Scripts Python: boto3 (compatível MinIO e S3)\ndbt: profiles.yml com targets dev (Postgres) e prod (Snowflake)\nBasta trocar o .env e rodar make pipeline novamente.", { x: 0.8, y: 4.55, w: 8.4, h: 0.65, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
  }

  // ================================================================
  // SLIDE 10 - CONCLUSÃO
  // ================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.bg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.08, fill: { color: C.accent } });

    s.addText("Conclusão", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, color: C.white, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.05, w: 1.5, h: 0.04, fill: { color: C.accent } });

    card(s, 0.5, 1.4, 4.2, 2.5, true);
    s.addText("Entregue", { x: 0.8, y: 1.55, w: 3.7, h: 0.35, fontSize: 15, color: C.green, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    const done = [
      { text: "Pipeline ELT completo (8 etapas)\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "NLP + Visão Computacional\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Naive Bayes hard-code + sklearn\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Dashboard Metabase automático\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "CloudFormation + integração AWS", options: { bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
    ];
    s.addText(done, { x: 0.8, y: 2.0, w: 3.7, h: 1.7, margin: 0 });

    card(s, 5.3, 1.4, 4.2, 2.5, true);
    s.addText("Próximos passos", { x: 5.6, y: 1.55, w: 3.7, h: 0.35, fontSize: 15, color: C.warn, fontFace: "Trebuchet MS", bold: true, margin: 0 });
    const next = [
      { text: "Treinar modelo com dados reais\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Dataset com mais notas extremas\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Balanceamento de classes\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Relatório final + apresentação\n", options: { breakLine: true, bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
      { text: "Testar com S3 e Snowflake reais", options: { bullet: true, fontSize: 11, color: C.muted, fontFace: "Calibri" } },
    ];
    s.addText(next, { x: 5.6, y: 2.0, w: 3.7, h: 1.7, margin: 0 });

    card(s, 0.5, 4.15, 9, 1.1);
    s.addText("Stack: Python · Docker · Airflow · dbt · PostgreSQL · MinIO · Metabase · AWS · Snowflake", { x: 0.8, y: 4.25, w: 8.4, h: 0.35, fontSize: 11, color: C.muted, fontFace: "Calibri", align: "center", margin: 0 });
    s.addText("Disciplinas: Aprendizagem de Máquina · Cloud Computing · Modelagem de Dados para IA", { x: 0.8, y: 4.6, w: 8.4, h: 0.3, fontSize: 11, color: C.accent, fontFace: "Calibri", align: "center", margin: 0 });
    s.addText("IFG — Pós-Graduação em Inteligência Artificial Aplicada — Módulo 2", { x: 0.8, y: 4.95, w: 8.4, h: 0.25, fontSize: 9, color: C.muted, fontFace: "Calibri", align: "center", margin: 0 });
  }

  await pres.writeFile({ fileName: "report/apresentacao.pptx" });
  console.log("Apresentacao gerada: report/apresentacao.pptx");
}

main().catch(e => { console.error(e); process.exit(1); });
