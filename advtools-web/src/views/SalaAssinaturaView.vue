<template>
  <div class="sala-assinatura" v-if="loaded">
    <!-- Navbar Pública -->
    <header class="public-nav">
      <div class="nav-brand">
        <i class="fas fa-pen-nib"></i>
        <span>ADVtools <strong>Sign</strong></span>
      </div>
      <div class="nav-badge">
        <i class="fas fa-lock"></i> Ambiente Seguro
      </div>
    </header>

    <!-- Erro -->
    <div v-if="error" class="error-container">
      <i class="fas fa-exclamation-triangle"></i>
      <h2>{{ error }}</h2>
      <p>Este link pode estar expirado ou inválido.</p>
    </div>

    <!-- Já Assinado -->
    <div v-else-if="jaAssinado" class="success-container">
      <i class="fas fa-check-circle"></i>
      <h2>Documento Assinado!</h2>
      <p>Sua assinatura foi registrada com sucesso.</p>
    </div>

    <!-- Sala Ativa -->
    <div v-else class="sala-content">
      <div class="welcome-bar">
        <div class="welcome-info">
          <span class="welcome-name">Olá, <strong>{{ signatario.nome }}</strong></span>
          <span class="welcome-role">{{ signatario.funcao }}</span>
        </div>
        <span class="doc-name">
          <i class="fas fa-file-pdf"></i> {{ documento.nome }}
        </span>
      </div>

      <div class="sala-grid">
        <!-- Visualizador Documento -->
        <div class="pdf-viewer-container">
          <div class="pdf-viewer-header">
            <span><i class="fas fa-eye"></i> Visualizar Documento</span>
            <div class="pdf-controls">
              <button class="btn-sm" @click="pdfPage = Math.max(1, pdfPage - 1)" :disabled="pdfPage <= 1">
                <i class="fas fa-chevron-left"></i>
              </button>
              <span class="page-info">Pág {{ pdfPage }} / {{ numPages }}</span>
              <button class="btn-sm" @click="pdfPage = Math.min(numPages, pdfPage + 1)" :disabled="pdfPage >= numPages">
                <i class="fas fa-chevron-right"></i>
              </button>
              <a :href="pdfUrl" target="_blank" class="download-btn" title="Abrir em nova aba">
                <i class="fas fa-external-link-alt"></i>
              </a>
            </div>
          </div>
          <div class="pdf-viewer-body">
            <div class="pdf-scroll-area">
              <VuePdfEmbed 
                v-if="pdfUrl" 
                :source="pdfUrl" 
                :page="pdfPage"
                @loaded="onPdfLoaded"
                class="pdf-canvas"
              />
            </div>
          </div>
        </div>

        <!-- Painel de Assinatura -->
        <div class="sign-panel">
          <!-- Tabs -->
          <div class="tab-header">
            <button
              :class="['tab-btn', { active: activeTab === 'desenho' }]"
              @click="activeTab = 'desenho'"
            >
              <i class="fas fa-pen"></i> Desenho Livre
            </button>
            <button
              :class="['tab-btn', { active: activeTab === 'selfie' }]"
              @click="activeTab = 'selfie'"
            >
              <i class="fas fa-camera"></i> Selfie
            </button>
          </div>

          <!-- Tab: Desenho -->
          <div v-show="activeTab === 'desenho'" class="tab-content">
            <p class="tab-desc">Assine com o dedo ou mouse na área abaixo:</p>
            <div class="canvas-container">
              <canvas
                ref="signCanvas"
                width="400"
                height="180"
                @mousedown="startDraw"
                @mousemove="draw"
                @mouseup="stopDraw"
                @mouseleave="stopDraw"
                @touchstart.prevent="startDrawTouch"
                @touchmove.prevent="drawTouch"
                @touchend="stopDraw"
              ></canvas>
            </div>
            <button class="btn-clear" @click="clearCanvas">
              <i class="fas fa-eraser"></i> Limpar
            </button>
          </div>

          <!-- Tab: Selfie -->
          <div v-show="activeTab === 'selfie'" class="tab-content">
            <p class="tab-desc">Tire uma selfie para autenticação:</p>
            <div class="camera-container">
              <video 
                ref="videoEl" 
                autoplay 
                playsinline 
                muted 
                class="camera-video" 
                v-show="!selfieCaptured"
              ></video>
              <canvas ref="selfieCanvas" class="selfie-preview" v-show="selfieCaptured"></canvas>
            </div>
            <div class="camera-actions">
              <div v-if="cameraError" class="camera-error">
                <i class="fas fa-exclamation-circle"></i>
                <p>{{ cameraError }}</p>
                <button @click="startCamera" class="btn-camera" style="margin-top: 10px;">
                  <i class="fas fa-redo"></i> Tentar Novamente
                </button>
              </div>
              <template v-else>
                <button v-if="!cameraActive" @click="startCamera" class="btn-camera">
                  <i class="fas fa-video"></i> Ativar Câmera
                </button>
                <button v-else-if="!selfieCaptured" @click="captureSelfie" class="btn-camera capture">
                  <i class="fas fa-camera"></i> Capturar
                </button>
                <button v-else @click="retakeSelfie" class="btn-clear">
                  <i class="fas fa-redo"></i> Tirar Novamente
                </button>
              </template>
            </div>
          </div>

          <!-- CPF -->
          <div class="cpf-section">
            <label>CPF (para constar no documento)</label>
            <input v-model="cpf" v-maska data-maska="###.###.###-##" type="text" placeholder="000.000.000-00" />
          </div>

          <!-- Consentimento -->
          <div class="consent-section">
            <label class="consent-label">
              <input type="checkbox" v-model="consentiu" />
              <span>Declaro que li o documento e concordo em assiná-lo digitalmente.</span>
            </label>
          </div>

          <!-- Confirmar -->
          <button
            class="btn-confirm"
            :disabled="!canConfirm || submitting"
            @click="confirmarAssinatura"
          >
            <i class="fas fa-check-double"></i>
            {{ submitting ? 'Enviando...' : 'Confirmar Assinatura' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { vMaska } from 'maska/vue'
import VuePdfEmbed from 'vue-pdf-embed'

const route = useRoute()
const tokenAccess = route.params.token as string
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const loaded = ref(false)
const error = ref('')
const jaAssinado = ref(false)
const submitting = ref(false)

const signatario = ref<any>({})
const documento = ref<any>({})
const pdfUrl = ref('')
const pdfPage = ref(1)
const numPages = ref(1)

const activeTab = ref('desenho')
const cpf = ref('')
const consentiu = ref(false)

// Canvas
const signCanvas = ref<HTMLCanvasElement | null>(null)
let ctx: CanvasRenderingContext2D | null = null
let isDrawing = false
let hasDrawn = false

// Camera / Selfie
const videoEl = ref<HTMLVideoElement | null>(null)
const selfieCanvas = ref<HTMLCanvasElement | null>(null)
const cameraActive = ref(false)
const selfieCaptured = ref(false)
let mediaStream: MediaStream | null = null

const canConfirm = computed(() => {
  if (!consentiu.value) return false
  if (activeTab.value === 'desenho') return hasDrawn
  if (activeTab.value === 'selfie') return selfieCaptured.value
  return false
})


async function loadSalaData() {
  try {
    const res = await fetch(`${API}/api/public/assinar/${tokenAccess}`)
    if (!res.ok) {
      error.value = 'Link inválido ou expirado'
      loaded.value = true
      return
    }
    const data = await res.json()
    signatario.value = data.signatario
    documento.value = data.documento
    
    if (signatario.value.cpf) cpf.value = signatario.value.cpf
    if (signatario.value.status === 'Assinado') jaAssinado.value = true

    pdfUrl.value = `${API}/api/public/assinar/preview-pdf/${data.documento.id}`
    loaded.value = true

    await nextTick()
    initCanvas()
  } catch (e) {
    error.value = 'Erro ao carregar dados'
    loaded.value = true
  }
}

function initCanvas() {
  if (!signCanvas.value) return
  ctx = signCanvas.value.getContext('2d')
  if (ctx) {
    ctx.lineWidth = 2.5
    ctx.lineCap = 'round'
    ctx.strokeStyle = '#1e293b'
  }
}

function getCanvasPos(e: MouseEvent) {
  const canvas = signCanvas.value!
  const rect = canvas.getBoundingClientRect()
  const scaleX = canvas.width / rect.width
  const scaleY = canvas.height / rect.height
  return { 
    x: (e.clientX - rect.left) * scaleX, 
    y: (e.clientY - rect.top) * scaleY 
  }
}
function getTouchPos(e: TouchEvent) {
  const canvas = signCanvas.value!
  const rect = canvas.getBoundingClientRect()
  const scaleX = canvas.width / rect.width
  const scaleY = canvas.height / rect.height
  const touch = e.touches[0]
  return { 
    x: ((touch?.clientX ?? 0) - rect.left) * scaleX, 
    y: ((touch?.clientY ?? 0) - rect.top) * scaleY 
  }
}

function startDraw(e: MouseEvent) { isDrawing = true; const p = getCanvasPos(e); ctx?.beginPath(); ctx?.moveTo(p.x, p.y); }
function draw(e: MouseEvent) { if (!isDrawing) return; hasDrawn = true; const p = getCanvasPos(e); ctx?.lineTo(p.x, p.y); ctx?.stroke(); }
function stopDraw() { isDrawing = false; ctx?.closePath(); }

function startDrawTouch(e: TouchEvent) { isDrawing = true; const p = getTouchPos(e); ctx?.beginPath(); ctx?.moveTo(p.x, p.y); }
function drawTouch(e: TouchEvent) { if (!isDrawing) return; hasDrawn = true; const p = getTouchPos(e); ctx?.lineTo(p.x, p.y); ctx?.stroke(); }

function clearCanvas() {
  if (!ctx || !signCanvas.value) return
  ctx.clearRect(0, 0, signCanvas.value.width, signCanvas.value.height)
  hasDrawn = false
}

const cameraError = ref('')

async function startCamera() {
  cameraError.value = ''
  try {
    // Usa constraints mínimas - sem facingMode nem resolução específica
    // Constraints muito específicas causam NotAllowedError no Chrome Android
    // antes mesmo do browser perguntar ao usuário sobre a permissão
    mediaStream = await navigator.mediaDevices.getUserMedia({ 
      video: true, 
      audio: false 
    })

    if (videoEl.value) {
      videoEl.value.srcObject = mediaStream
      await videoEl.value.play().catch(e => console.warn('Autoplay falhou:', e))
    }
    cameraActive.value = true
  } catch (e: any) {
    console.error('Erro ao abrir câmera:', e.name, e.message)
    if (e.name === 'NotAllowedError') {
      cameraError.value = 'Permissão negada. Verifique as configurações de câmera do seu navegador e tente novamente.'
    } else if (e.name === 'NotFoundError') {
      cameraError.value = 'Nenhuma câmera encontrada no dispositivo.'
    } else {
      cameraError.value = `Erro ao acessar câmera: ${e.message}`
    }
  }
}

function onPdfLoaded(pdf: any) {
  numPages.value = pdf.numPages
}

function captureSelfie() {
  if (!videoEl.value || !selfieCanvas.value) return
  const video = videoEl.value
  const canvas = selfieCanvas.value
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  const sctx = canvas.getContext('2d')
  sctx?.drawImage(video, 0, 0)
  selfieCaptured.value = true
  // Stop camera
  mediaStream?.getTracks().forEach(t => t.stop())
}

function retakeSelfie() {
  selfieCaptured.value = false
  startCamera()
}

function getImageBase64(): string {
  if (activeTab.value === 'desenho' && signCanvas.value) {
    return signCanvas.value.toDataURL('image/png')
  }
  if (activeTab.value === 'selfie' && selfieCanvas.value) {
    return selfieCanvas.value.toDataURL('image/png')
  }
  return ''
}

async function confirmarAssinatura() {
  submitting.value = true
  const imgB64 = getImageBase64()
  if (!imgB64) {
    alert('Nenhuma imagem capturada.')
    submitting.value = false
    return
  }

  try {
    const res = await fetch(`${API}/api/public/assinar/${tokenAccess}/confirmar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        imagem_base64: imgB64,
        cpf: cpf.value,
        tipo_autenticacao: activeTab.value === 'desenho' ? 'assinatura' : 'selfie'
      })
    })
    if (res.ok) {
      jaAssinado.value = true
    } else {
      const err = await res.json()
      alert(err.detail || 'Erro ao confirmar assinatura')
    }
  } catch (e) {
    alert('Erro de conexão')
  }
  submitting.value = false
}

onMounted(loadSalaData)
onBeforeUnmount(() => {
  mediaStream?.getTracks().forEach(t => t.stop())
})
</script>

<style scoped>
.sala-assinatura {
  min-height: 100vh;
  background: #f0f4f8;
  font-family: 'Inter', sans-serif;
}

/* Navbar */
.public-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  color: #fff;
  padding: 16px 30px;
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
}
.nav-brand i { color: #60a5fa; }
.nav-badge {
  background: rgba(255,255,255,0.1);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.8rem;
}
.nav-badge i { color: #34d399; margin-right: 5px; }

/* Error / Success containers */
.error-container, .success-container {
  text-align: center;
  padding: 80px 20px;
}
.error-container i { font-size: 4rem; color: #dc2626; }
.error-container h2 { color: #1e293b; }
.success-container i { font-size: 4rem; color: #16a34a; }
.success-container h2 { color: #1e293b; }

/* Welcome Bar */
.welcome-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 16px 24px;
  margin: 20px 24px 0;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.welcome-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.welcome-name { font-size: 1rem; color: #1e293b; }
.welcome-role {
  background: #eff6ff;
  color: #2563eb;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}
.doc-name {
  color: #64748b;
  font-size: 0.9rem;
}
.doc-name i { color: #dc2626; margin-right: 5px; }

/* Grid */
.sala-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px;
  padding: 20px 24px;
}

/* PDF Viewer */
.pdf-viewer-container {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.pdf-viewer-header {
  padding: 12px 18px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-weight: 600;
  font-size: 0.85rem;
  color: #475569;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pdf-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}
.page-info {
  font-size: 0.8rem;
  color: #64748b;
  min-width: 80px;
  text-align: center;
}
.pdf-viewer-body {
  background: #f1f5f9;
  display: flex;
  justify-content: center;
}
.pdf-scroll-area {
  width: 100%;
  max-height: 70vh;
  overflow-y: auto;
  display: flex;
  justify-content: center;
  padding: 10px;
}
.pdf-canvas {
  max-width: 100%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.btn-sm {
  background: #fff;
  border: 1px solid #e2e8f0;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-sm:hover:not(:disabled) { background: #f8fafc; border-color: #cbd5e1; }
.btn-sm:disabled { opacity: 0.5; cursor: not-allowed; }

/* Sign Panel */
.sign-panel {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
}

.tab-header {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.tab-btn {
  flex: 1;
  padding: 10px;
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  color: #64748b;
  transition: all 0.2s;
}
.tab-btn.active {
  background: #eff6ff;
  border-color: #2563eb;
  color: #2563eb;
}
.tab-btn:hover { background: #f8fafc; }

.tab-content { margin-bottom: 16px; }
.tab-desc { font-size: 0.82rem; color: #64748b; margin: 0 0 10px; }

/* Canvas */
.canvas-container {
  border: 2px dashed #cbd5e1;
  border-radius: 10px;
  overflow: hidden;
  background: #fefefe;
  margin-bottom: 8px;
}
.canvas-container canvas {
  width: 100%;
  height: 180px;
  cursor: crosshair;
  touch-action: none;
}
.btn-clear {
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  padding: 6px 14px;
  cursor: pointer;
  font-size: 0.8rem;
  color: #64748b;
}
.btn-clear:hover { background: #e2e8f0; }

/* Camera */
.camera-container {
  border-radius: 10px;
  overflow: hidden;
  background: #000;
  margin-bottom: 10px;
  aspect-ratio: 4/3;
  display: flex;
  align-items: center;
  justify-content: center;
}
.camera-video, .selfie-preview {
  width: 100%;
  max-height: 250px;
  object-fit: cover;
}
.camera-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  justify-content: center;
}
.camera-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  padding: 14px;
  text-align: center;
  color: #991b1b;
  font-size: 0.85rem;
}
.camera-error i { font-size: 1.4rem; margin-bottom: 6px; display: block; }
.camera-error p { margin: 0 0 4px; }
.btn-camera {
  background: #1e293b;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
}
.btn-camera.capture { background: #dc2626; }
.btn-camera:hover { opacity: 0.9; }

/* CPF */
.cpf-section {
  margin-bottom: 12px;
}
.cpf-section label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 4px;
}
.cpf-section input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-sizing: border-box;
}

/* Consent */
.consent-section {
  margin-bottom: 16px;
}
.consent-label {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 0.82rem;
  color: #475569;
  cursor: pointer;
}
.consent-label input[type="checkbox"] {
  margin-top: 2px;
  accent-color: #2563eb;
}

/* Confirm Button */
.btn-confirm {
  background: linear-gradient(135deg, #16a34a, #15803d);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 14px;
  width: 100%;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-confirm:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(22,163,74,0.3); }
.btn-confirm:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

@media (max-width: 900px) {
  .sala-grid { 
    grid-template-columns: 1fr; 
    padding: 10px;
  }
  .welcome-bar { 
    flex-direction: column; 
    gap: 12px; 
    align-items: flex-start; 
    margin: 10px 10px 0;
  }
  .pdf-scroll-area {
    max-height: 50vh;
  }
  .sign-panel {
    padding: 15px;
  }
}

.download-btn {
  font-size: 0.8rem;
  color: #2563eb;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 6px;
  background: #eff6ff;
  transition: background 0.2s;
}
.download-btn:hover { background: #dbeafe; }
</style>
