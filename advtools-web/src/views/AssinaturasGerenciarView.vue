<template>
  <div class="gerenciar-assinaturas">
    <div class="page-header">
      <div class="header-left">
        <!-- Breadcrumb -->
        <div class="breadcrumb">
          <router-link v-if="clienteId" :to="`/clientes/${clienteId}`" class="breadcrumb-link">
            <i class="fas fa-arrow-left"></i> {{ clienteNome || 'Cliente' }}
          </router-link>
          <button v-else class="btn-back" @click="$router.back()">
            <i class="fas fa-arrow-left"></i>
          </button>
          <span class="breadcrumb-sep">/</span>
          <span class="breadcrumb-current">Assinaturas</span>
        </div>
        <div>
          <h2>Gerenciar Assinaturas</h2>
          <p class="subtitle" v-if="documento" style="display: flex; align-items: center; gap: 6px;">
            <i :class="[getFileIconClass(documento.arquivo_path), getFileIconTextColor(documento.arquivo_path)]"></i>
            {{ documento.nome }}
            <span class="text-[0.65rem] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ml-1" :class="getFileBadgeClass(documento.arquivo_path)">
                {{ getFileExtension(documento.arquivo_path) }}
            </span>
          </p>
        </div>
      </div>
      <div class="header-right" style="display: flex; flex-direction: column; align-items: flex-end; gap: 10px;">
        <span :class="['status-badge', statusClass]">
          <i :class="statusIcon"></i> {{ statusLabel }}
        </span>
        <div class="flex items-center gap-2" v-if="documento" style="display: flex; gap: 8px;">
          <a :href="getStaticUrl(documento.arquivo_path)" target="_blank" class="px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 border border-slate-300 rounded-md hover:bg-slate-200 transition-colors flex items-center gap-1 shadow-sm" style="text-decoration: none;" title="Baixar Original">
            <i class="fas fa-file-download"></i> Original
          </a>
          <a v-if="documento.status_assinatura === 'Concluido' && documento.arquivo_assinado_path" :href="getStaticUrl(documento.arquivo_assinado_path)" target="_blank" class="px-3 py-1.5 text-xs font-semibold text-white bg-green-600 border border-green-700 rounded-md hover:bg-green-700 transition-colors flex items-center gap-1 shadow-sm" style="text-decoration: none;" title="Baixar Assinado">
            <i class="fas fa-file-signature"></i> Finalizado
          </a>
        </div>
      </div>
    </div>

    <div class="content-grid">
      <!-- Coluna: Adicionar Signatário -->
      <div class="card add-signer-card">
        <div class="card-header">
          <i class="fas fa-user-plus"></i>
          <h3>Adicionar Signatário</h3>
        </div>

        <div class="quick-add-section" v-if="quickContacts.length > 0">
          <p class="quick-add-title">Adição Rápida (1 clique)</p>
          <div class="quick-add-chips">
            <button
              v-for="(ct, idx) in quickContacts" :key="idx"
              type="button" 
              class="quick-add-chip"
              @click="addQuickContact(ct)"
              title="Adicionar como signatário"
            >
              <i class="fas fa-user-plus"></i>
              <span class="chip-name">{{ ct.nome.split(' ')[0] }}</span>
              <span class="chip-role">{{ ct.tipo }}</span>
            </button>
          </div>
        </div>
        
        <div class="form-divider" v-if="quickContacts.length > 0">ou digite os dados manualmente</div>

        <form @submit.prevent="addSignatario" class="signer-form">
          <div class="form-group">
            <label>Nome Completo</label>
            <input v-model="newSigner.nome" type="text" placeholder="Ex: João da Silva" required />
          </div>
          <div class="form-group">
            <label>E-mail</label>
            <input v-model="newSigner.email" type="email" placeholder="joao@email.com" required />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>CPF (Opcional)</label>
              <input v-model="newSigner.cpf" type="text" placeholder="000.000.000-00" />
            </div>
            <div class="form-group">
              <label>Função</label>
              <select v-model="newSigner.funcao">
                <option value="Parte">Parte</option>
                <option value="Testemunha">Testemunha</option>
                <option value="Advogado">Advogado</option>
                <option value="Representante Legal">Representante Legal</option>
              </select>
            </div>
          </div>
          <button type="submit" class="btn-primary" :disabled="loading">
            <i class="fas fa-plus"></i> Adicionar
          </button>
        </form>
      </div>

      <!-- Coluna: Lista de Signatários -->
      <div class="card signers-list-card">
        <div class="card-header" style="justify-content: space-between;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-users"></i>
            <h3>Signatários ({{ signatarios.length }})</h3>
          </div>
          <button v-if="signatarios.length > 0 && documento?.status_assinatura !== 'Concluido'" class="btn-outline-primary btn-sm" @click="openPosModal">
            <i class="fas fa-crosshairs"></i> Posicionar
          </button>
        </div>

        <div v-if="signatarios.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>Nenhum signatário adicionado.</p>
          <small>Adicione signatários usando o formulário ao lado.</small>
        </div>

        <ul class="signers-list" v-else>
          <li v-for="sig in signatarios" :key="sig.id" class="signer-item">
            <div class="signer-info">
              <div class="signer-name">
                <strong>{{ sig.nome }}</strong>
                <span class="signer-role">{{ sig.funcao }}</span>
              </div>
              <span class="signer-email">{{ sig.email }}</span>
              <span :class="['signer-badge', 'badge-' + sig.status.toLowerCase()]">
                {{ sig.status }}
              </span>
            </div>

            <div class="signer-actions">
              <!-- Link de Assinatura -->
              <div class="link-box" @click="copyLink(sig.token_acesso)" :title="'Copiar link'">
                <i class="fas fa-link"></i>
                <span class="link-text">{{ getSignLink(sig.token_acesso) }}</span>
              </div>
              <div class="action-buttons">
                <a :href="getWhatsAppLink(sig)" target="_blank" class="btn-whatsapp" title="Enviar por WhatsApp">
                  <i class="fab fa-whatsapp"></i>
                </a>
                <button v-if="sig.status !== 'Assinado'" @click="removeSignatario(sig.id)" class="btn-danger-sm" title="Remover">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </li>
        </ul>


        <div v-if="documento?.status_assinatura === 'Concluido'" class="finalize-section completed">
          <i class="fas fa-check-circle"></i> Documento Concluído
        </div>
      </div>
    </div>

    <!-- Modal Posicionamento -->
    <div v-if="posModal.show" class="modal-overlay">
      <div class="modal-content modal-large">
        <div class="modal-header">
          <h3>Posicionar Assinaturas</h3>
          <button class="btn-close" @click="closePosModal"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body pos-body">
          <div class="pos-sidebar">
            <h4>Selecione o Signatário</h4>
            <ul class="pos-signers">
              <li 
                v-for="sig in signatarios" 
                :key="sig.id"
                :class="['pos-signer-item', { active: posModal.activeSigner?.id === sig.id }]"
                @click="activateSignerForPos(sig)"
              >
                <div class="sig-name">{{ sig.nome }}</div>
                <div class="sig-role">{{ sig.funcao }}</div>
                <div v-if="sig.posicionou" class="sig-status-ok"><i class="fas fa-check"></i> Posicionado</div>
                
                <!-- MOVIDO PARA CÁ: Botão ficará logo abaixo do signatário se ele for o selecionado -->
                <div v-if="posModal.activeSigner?.id === sig.id" style="margin-top: 10px;">
                  <button class="btn-primary btn-sm" @click.stop="addStampToCurrentPage" style="width: 100%; border-radius: 4px;">
                    <i class="fas fa-plus"></i> Inserir Carimbo Aqui
                  </button>
                </div>
              </li>
            </ul>
            <div class="pos-tips">
              <p>1. Selecione um signatário acima</p>
              <p>2. Clique em <b>Inserir Carimbo</b></p>
              <p>3. Arraste a caixa para a posição e confirme</p>
            </div>
          </div>
          <div class="pos-viewer">
            <div class="pdf-toolbar">
              <button class="btn-sm" @click="posPage = Math.max(1, posPage - 1)" :disabled="posPage <= 1"><i class="fas fa-chevron-left"></i> Ant</button>
              <span>Página {{ posPage }} de {{ numPages }}</span>
              <button class="btn-sm" @click="posPage = Math.min(numPages, posPage + 1)" :disabled="posPage >= numPages">Próx <i class="fas fa-chevron-right"></i></button>
            </div>
            
            <div class="pdf-scroll-area">
              <div class="pdf-page-wrapper" ref="pdfContainerRef">
                <VuePdfEmbed v-if="pdfUrl" :source="pdfUrl" :page="posPage" @rendered="onPdfRendered" @loaded="onPdfLoaded" />
                
                <!-- Draggable Stamps Layer -->
                <div 
                  v-for="(stamp, sIdx) in posModal.stamps" 
                  :key="stamp.id || sIdx"
                  v-show="stamp.page === posPage"
                  :class="['draggable-stamp', { 'dragging': activeDragStamp === stamp }]"
                  :style="{ left: stamp.x + 'px', top: stamp.y + 'px', width: stamp.w + 'px', height: stamp.h + 'px' }"
                  @mousedown.prevent="startDragStamp($event, stamp)"
                >
                  <button @click.stop="removeStamp(sIdx)" class="btn-remove-stamp" title="Remover Assinatura"><i class="fas fa-times"></i></button>
                  <div class="stamp-content">
                    <div class="s-by">Assinado por:</div>
                    <div class="s-name">{{ stamp.nome }}</div>
                    <div class="s-doc">CPF: {{ stamp.cpf || 'Não inf.' }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="pos-actions">
               <span v-if="posModal.activeSigner">Posicionando assinatura de <b>{{ posModal.activeSigner.nome }}</b></span>
               <span v-else><b>Selecione um signatário à esquerda para começar a posicionar.</b></span>
               <div style="display: flex; gap: 10px; align-items: center;">
                 <button class="btn-cancel-confirm" style="padding: 6px 16px;" @click="closePosModal">Fechar</button>
                 <button class="btn-primary" @click="savePositions" :disabled="savingPositions || !posModal.activeSigner" style="padding: 6px 16px;">
                    <i class="fas fa-save"></i> {{ savingPositions ? 'Salvando...' : 'Salvar Posições' }}
                 </button>
               </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast.show" :class="['toast', toast.type]">
      {{ toast.message }}
    </div>

    <!-- Confirm Dialog -->
    <div v-if="confirmDialog.show" class="confirm-overlay">
      <div class="confirm-box">
        <div class="confirm-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h3>Confirmar</h3>
        <p>{{ confirmDialog.message }}</p>
        <div class="confirm-actions">
          <button @click="confirmDialog.show = false" class="btn-cancel-confirm">Cancelar</button>
          <button @click="executeConfirmDialog" class="btn-do-confirm">Confirmar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import VuePdfEmbed from 'vue-pdf-embed'

const route = useRoute()
const documentoId = Number(route.params.id)
const clienteId = route.query.clienteId as string
const clienteNome = route.query.clienteNome as string
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_BASE = '' // kept for internal routing proxy if any, but Vite proxy handles `/api` ok. Wait, we usually use empty string for frontend proxy to `/api`. Let's stick to empty string for API calls.

const documento = ref<any>(null)
const signatarios = ref<any[]>([])
const loading = ref(false)
const newSigner = ref({ nome: '', email: '', cpf: '', funcao: 'Parte' })
const toast = ref({ show: false, message: '', type: 'success' })

const token = localStorage.getItem('advtools_token')
const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }

// Confirm dialog
const confirmDialog = ref({ show: false, message: '', onConfirm: null as (() => void) | null })
function askConfirm(message: string, onConfirm: () => void) {
  confirmDialog.value = { show: true, message, onConfirm }
}
function executeConfirmDialog() {
  if (confirmDialog.value.onConfirm) confirmDialog.value.onConfirm()
  confirmDialog.value.show = false
}

const statusClass = computed(() => {
  const st = documento.value?.status_assinatura
  if (st === 'Concluido') return 'status-success'
  if (st === 'Parcial') return 'status-warning'
  return 'status-pending'
})
const statusIcon = computed(() => {
  const st = documento.value?.status_assinatura
  if (st === 'Concluido') return 'fas fa-check-circle'
  return 'fas fa-clock'
})
const statusLabel = computed(() => documento.value?.status_assinatura || 'Aguardando')

function showToast(message: string, type = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => toast.value.show = false, 3000)
}

function getStaticUrl(path: string) {
  if (!path) return '#'
  if (path.startsWith('http')) return path
  let cleanPath = path
  // Suporte a arquivos legados sem o prefixo armazenamento/
  if (!cleanPath.startsWith('armazenamento/') && !cleanPath.startsWith('static/')) {
    cleanPath = `armazenamento/${cleanPath}`
  }
  return `${API}/static/${cleanPath}`
}

async function loadData() {
  try {
    const docRes = await fetch(`${API_BASE}/api/documentos/${documentoId}`, { headers })
    if (docRes.ok) {
      documento.value = await docRes.json()
    } else {
      documento.value = { id: documentoId, nome: `Documento #${documentoId}`, status_assinatura: 'Aguardando' }
    }
    
    const sigRes = await fetch(`${API_BASE}/api/documentos/${documentoId}/signatarios`, { headers })
    if (sigRes.ok) {
      signatarios.value = await sigRes.json()
    }
  } catch (e) {
    console.error('Erro ao carregar dados:', e)
  }
}

async function addSignatario() {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/documentos/${documentoId}/signatarios`, {
      method: 'POST',
      headers,
      body: JSON.stringify(newSigner.value)
    })
    if (res.ok) {
      showToast('Signatário adicionado!')
      newSigner.value = { nome: '', email: '', cpf: '', funcao: 'Parte' }
      await loadData()
    } else {
      const err = await res.json()
      showToast(err.detail || 'Erro ao adicionar', 'error')
    }
  } catch (e) {
    showToast('Erro de conexão', 'error')
  }
  loading.value = false
}

async function removeSignatario(sigId: number) {
  askConfirm('Tem certeza que deseja remover este signatário?', async () => {
    try {
      const res = await fetch(`${API_BASE}/api/documentos/${documentoId}/signatarios/${sigId}`, {
        method: 'DELETE',
        headers
      })
      if (res.ok) {
        showToast('Signatário removido')
        await loadData()
      } else {
        const err = await res.json().catch(() => ({}))
        showToast(err.detail || 'Erro ao remover signatário', 'error')
      }
    } catch (e) {
      showToast('Erro de conexão', 'error')
    }
  })
}



function getSignLink(tokenAccess: string) {
  return `${window.location.origin}/assinar/${tokenAccess}`
}

function copyLink(tokenAccess: string) {
  const link = getSignLink(tokenAccess)
  navigator.clipboard.writeText(link)
  showToast('Link copiado!')
}

function getWhatsAppLink(sig: any) {
  const link = getSignLink(sig.token_acesso)
  const text = `Olá ${sig.nome.split(' ')[0]}, por favor assine o documento no link: ${link}`
  return `https://wa.me/?text=${encodeURIComponent(text)}`
}

// === QUICK ADD CONTACTS ===
const quickContacts = ref<any[]>([])

async function loadQuickContacts() {
  if (!clienteId) return;
  try {
    // Carrega Equipe
    const reqEquipe = await fetch(`${API_BASE}/api/usuarios`, { headers })
    if (reqEquipe.ok) {
      const equipe = await reqEquipe.json()
      equipe.forEach((u: any) => {
        quickContacts.value.push({
          nome: u.nome, email: u.email, cpf: u.cpf, funcao: 'Testemunha', tipo: 'Equipe'
        })
      })
    }
    // Carrega Cliente
    const reqCliente = await fetch(`${API_BASE}/api/clientes/${clienteId}`, { headers })
    if (reqCliente.ok) {
      const c = await reqCliente.json()
      quickContacts.value.push({
        nome: c.nome, email: c.email || '', cpf: c.documento || '', funcao: 'Parte', tipo: 'Cliente'
      })
    }
    // Carrega Partes
    const reqPartes = await fetch(`${API_BASE}/api/clientes/${clienteId}/partes`, { headers })
    if (reqPartes.ok) {
      const partes = await reqPartes.json()
      partes.forEach((p: any) => {
        quickContacts.value.push({
          nome: p.nome, email: p.email || '', cpf: p.documento || '', funcao: p.papel || 'Parte', tipo: 'Parte Envolvida'
        })
      })
    }
  } catch(e) { 
    console.error('Erro ao carregar contatos rápidos', e) 
  }
}

async function addQuickContact(ct: any) {
  newSigner.value = {
    nome: ct.nome || '',
    email: ct.email || '',
    cpf: ct.cpf || '',
    funcao: ct.funcao || 'Parte'
  }
  if (!ct.email) {
    showToast('Por favor, informe o e-mail antes de adicionar', 'warning')
    return; // User precisa digitar o email que falta
  }
  await addSignatario()
}

// --- Funções de Ícones e Tipos de Arquivo ---
function getFileExtension(path: string | undefined): string {
    if (!path) return 'pdf';
    const parts = path.split('.');
    if (parts.length > 1) {
        const lastPart = parts.pop();
        return lastPart ? lastPart.toLowerCase() : 'pdf';
    }
    return 'pdf';
}

function getFileIconClass(path: string | undefined) {
    const ext = getFileExtension(path);
    if (ext === 'pdf') return 'fas fa-file-pdf';
    if (ext === 'doc' || ext === 'docx') return 'fas fa-file-word';
    return 'fas fa-file-alt';
}

function getFileIconTextColor(path: string | undefined) {
    const ext = getFileExtension(path);
    if (ext === 'pdf') return 'color-red'; // Usamos classes custom ou style se preferir
    if (ext === 'doc' || ext === 'docx') return 'color-blue';
    return 'color-slate';
}

function getFileBadgeClass(path: string | undefined) {
    const ext = getFileExtension(path);
    if (ext === 'pdf') return 'badge-pdf';
    if (ext === 'doc' || ext === 'docx') return 'badge-word';
    return 'badge-generic';
}
// ==========================

// === MODAL POSICIONAMENTO ===
const posModal = ref({
  show: false,
  activeSigner: null as any,
  stamps: [] as any[] // { sigId, nome, cpf, page, x, y, w, h }
})
const pdfUrl = ref('')
const posPage = ref(1)
const numPages = ref(1)
const savingPositions = ref(false)
const pdfContainerRef = ref<HTMLElement | null>(null)

async function openPosModal() {
  posModal.value.show = true
  posModal.value.activeSigner = null
  posPage.value = 1
  
  // Limpa stamps e reconstroi baseado nas multiplas posicoes de cada signatario
  posModal.value.stamps = []
  
  signatarios.value.forEach(s => {
    if (s.posicoes && s.posicoes.length > 0) {
      s.posicoes.forEach((p: any) => {
        posModal.value.stamps.push({
          sigId: s.id,
          nome: s.nome,
          cpf: s.cpf,
          page: p.page_number || 1,
          x: p.x_pos || 20,
          y: p.y_pos || 20,
          w: p.width || 130,
          h: p.height || 40
        })
      })
    }
  })

  pdfUrl.value = `${API_BASE}/api/public/assinar/preview-pdf/${documentoId}`
}

function closePosModal() {
  posModal.value.show = false
}

function activateSignerForPos(sig: any) {
  posModal.value.activeSigner = sig
  // Removido o pulo de página automático para permitir o usuário posicionar na página atual que ele estiver visualizando
}

function addStampToCurrentPage() {
  if (!posModal.value.activeSigner) return
  const sig = posModal.value.activeSigner
  posModal.value.stamps.push({
    id: Date.now() + Math.random(), // gerando key local unicamente pro loop frontend
    sigId: sig.id,
    nome: sig.nome,
    cpf: sig.cpf,
    page: posPage.value,
    x: 100, // Centralizado um pouco mais pro meio da tela (assume 600px default pdf view width)
    y: 100,
    w: 120, // Largura fina 
    h: 30   // Altura mínima representativa
  })
}

function removeStamp(idx: number) {
  posModal.value.stamps.splice(idx, 1)
}

function onPdfLoaded(source: any) {
  numPages.value = source.numPages
}
function onPdfRendered() {
  // Chamado quando o canvas é renderizado
}

let activeDragStamp: any = null
let dragStartX = 0
let dragStartY = 0
let initialStampX = 0
let initialStampY = 0
const activeDragStampRef = ref<any>(null) // Using ref to trigger computed class reactivity

function startDragStamp(event: MouseEvent, stamp: any) {
  if (posModal.value.activeSigner?.id !== stamp.sigId) {
    // Auto-activate signer se clicar em um stamp que seja dele
    const sig = signatarios.value.find(s => s.id === stamp.sigId)
    if (sig) activateSignerForPos(sig)
  }
  
  activeDragStamp = stamp
  activeDragStampRef.value = stamp
  dragStartX = event.clientX
  dragStartY = event.clientY
  initialStampX = stamp.x
  initialStampY = stamp.y
  
  document.addEventListener('mousemove', onDragStampMove)
  document.addEventListener('mouseup', onDragStampEnd)
}

function onDragStampMove(event: MouseEvent) {
  if (!activeDragStamp) return
  
  const dx = event.clientX - dragStartX
  const dy = event.clientY - dragStartY
  
  activeDragStamp.x = Math.max(0, initialStampX + dx)
  activeDragStamp.y = Math.max(0, initialStampY + dy)
}

function onDragStampEnd() {
  if (activeDragStamp) {
    const sigIdx = signatarios.value.findIndex(s => s.id === activeDragStamp.sigId)
    if (sigIdx > -1) signatarios.value[sigIdx].posicionou = true
  }
  activeDragStamp = null
  activeDragStampRef.value = null
  document.removeEventListener('mousemove', onDragStampMove)
  document.removeEventListener('mouseup', onDragStampEnd)
}

async function savePositions() {
  savingPositions.value = true
  if (!pdfContainerRef.value) return

  const rect = pdfContainerRef.value.getBoundingClientRect()
  const docVisualW = rect.width
  const docVisualH = rect.height

  try {
    const stampsBySig: Record<string, any[]> = {}
    
    // Assegura que signatarios sem posições também enviem array vazio se precisar atualizar
    signatarios.value.forEach(s => { stampsBySig[s.id.toString()] = [] })
    
    // Organiza todos os selos
    posModal.value.stamps.forEach(st => {
      const sid = st.sigId.toString()
      if (!stampsBySig[sid]) stampsBySig[sid] = []
      stampsBySig[sid].push({
        page_number: st.page,
        x_pos: st.x,
        y_pos: st.y,
        width: st.w,
        height: st.h,
        docWidth: docVisualW,
        docHeight: docVisualH
      })
    })

    const promises = Object.keys(stampsBySig).map(sigIdstr => {
      const sigId = parseInt(sigIdstr)
      return fetch(`${API_BASE}/api/documentos/${documentoId}/signatarios/${sigId}/posicao`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ posicoes: stampsBySig[sigId] })
      })
    })

    await Promise.all(promises)
    showToast('Posições salvas com sucesso!')
    closePosModal()
    await loadData()
  } catch (e) {
    showToast('Erro ao salvar posições', 'error')
  }
  savingPositions.value = false
}
// ==================================

onMounted(async () => {
  await loadData()
  loadQuickContacts()
})
</script>

<style scoped>
.gerenciar-assinaturas {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex-direction: column;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
}
.breadcrumb-link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: color 0.2s;
}
.breadcrumb-link:hover { color: #1d4ed8; }
.breadcrumb-sep { color: #cbd5e1; }
.breadcrumb-current { color: #64748b; font-weight: 500; }

.header-left h2 {
  margin: 0;
  font-size: 1.6rem;
  color: #1e293b;
}

.subtitle {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
}

.btn-back {
  background: #f1f5f9;
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
  font-size: 1.1rem;
  color: #64748b;
  transition: all 0.2s;
}
.btn-back:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}
.status-success { background: #dcfce7; color: #166534; }
.status-warning { background: #fef3c7; color: #92400e; }
.status-pending { background: #f1f5f9; color: #64748b; }

.content-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 24px;
}

.card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}
.card-header i {
  color: #2563eb;
  font-size: 1.1rem;
}
.card-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1e293b;
}

.signer-form .form-group {
  margin-bottom: 14px;
}
.signer-form label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 5px;
}
.signer-form input, .signer-form select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: border 0.2s;
  box-sizing: border-box;
}
.signer-form input:focus, .signer-form select:focus {
  border-color: #2563eb;
  outline: none;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.btn-primary {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(37,99,235,0.3); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

/* Quick Add Styles */
.quick-add-section {
  margin-bottom: 20px;
}
.quick-add-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 10px;
}
.quick-add-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.quick-add-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 6px 12px;
  font-size: 0.8rem;
  color: #334155;
  cursor: pointer;
  transition: all 0.2s;
}
.quick-add-chip:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}
.quick-add-chip i {
  color: #2563eb;
  font-size: 0.75rem;
}
.chip-name {
  font-weight: 600;
}
.chip-role {
  font-size: 0.65rem;
  color: #64748b;
  background: #fff;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 2px;
}
.form-divider {
  text-align: center;
  font-size: 0.8rem;
  color: #94a3b8;
  margin-bottom: 20px;
  position: relative;
}
.form-divider::before, .form-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 20%;
  height: 1px;
  background: #e2e8f0;
}
.form-divider::before { left: 0; }
.form-divider::after { right: 0; }

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #94a3b8;
}
.empty-state i { font-size: 2.5rem; margin-bottom: 10px; }
.empty-state p { margin: 5px 0; }

.signers-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.signer-item {
  padding: 16px;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  margin-bottom: 12px;
  transition: all 0.2s;
}
.signer-item:hover {
  border-color: #e2e8f0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.signer-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.signer-name {
  display: flex;
  align-items: center;
  gap: 8px;
}
.signer-role {
  font-size: 0.75rem;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
}
.signer-email {
  color: #64748b;
  font-size: 0.85rem;
}
.signer-badge {
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  margin-left: auto;
}
.badge-pendente { background: #fee2e2; color: #991b1b; }
.badge-visualizado { background: #e0f2fe; color: #075985; }
.badge-assinado { background: #dcfce7; color: #166534; }

.signer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.link-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8fafc;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
  flex: 1;
  margin-right: 10px;
  overflow: hidden;
}
.link-box:hover { background: #e0f2fe; }
.link-box i { color: #2563eb; font-size: 0.8rem; }
.link-text {
  font-family: monospace;
  font-size: 0.75rem;
  color: #475569;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-buttons {
  display: flex;
  gap: 8px;
}
.btn-whatsapp {
  background: #25d366;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 1rem;
  text-decoration: none;
  display: flex;
  align-items: center;
}
.btn-whatsapp:hover { background: #20ba5c; }

.btn-danger-sm {
  background: #fee2e2;
  color: #dc2626;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}
.btn-danger-sm:hover { background: #dc2626; color: #fff; }

.finalize-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
  text-align: center;
}
.finalize-section.completed {
  color: #166534;
  font-weight: 600;
  font-size: 1.1rem;
}
.btn-finalize {
  background: linear-gradient(135deg, #16a34a, #15803d);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 14px 30px;
  font-weight: 600;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}
.btn-finalize:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(22,163,74,0.3); }

.toast {
  position: fixed;
  bottom: 30px;
  right: 30px;
  padding: 14px 24px;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}
.toast.success { background: #16a34a; }
.toast.error { background: #dc2626; }
@keyframes slideIn {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@media (max-width: 768px) {
  .content-grid { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 10px; }
}

/* Confirm Dialog */
.confirm-overlay {
  position: fixed;
  inset: 0;
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
}
.confirm-box {
  background: #fff;
  border-radius: 16px;
  padding: 32px 28px;
  max-width: 380px;
  width: calc(100% - 40px);
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}
.confirm-icon i {
  font-size: 2.5rem;
  color: #f59e0b;
  margin-bottom: 12px;
}
.confirm-box h3 { margin: 0 0 8px; color: #1e293b; font-size: 1.1rem; }
.confirm-box p { color: #64748b; font-size: 0.9rem; margin: 0 0 24px; }
.confirm-actions { display: flex; gap: 10px; justify-content: center; }
.btn-cancel-confirm {
  padding: 10px 22px;
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  color: #64748b;
  transition: all 0.2s;
}
.btn-cancel-confirm:hover { background: #f8fafc; }
.btn-do-confirm {
  padding: 10px 22px;
  background: #dc2626;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-do-confirm:hover { background: #b91c1c; }

/* Modal de Posicionamento */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content.modal-large {
  width: 90%;
  max-width: 1100px;
  height: 90vh;
  background: #fff;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}
.modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
}
.modal-header h3 { margin: 0; font-size: 1.2rem; color: #1e293b; }
.btn-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #64748b;
  cursor: pointer;
}
.btn-sm {
  background: #fff;
  border: 1px solid #cbd5e1;
  padding: 6px 12px;
  font-size: 0.85rem;
  border-radius: 6px;
  cursor: pointer;
}
.btn-primary.btn-sm {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  border: none;
}
.pos-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.pos-sidebar {
  width: 280px;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
  padding: 20px;
  display: flex;
  flex-direction: column;
}
.pos-sidebar h4 { margin: 0 0 16px; color: #1e293b; font-size: 1rem; }
.pos-signers {
  list-style: none;
  padding: 0; margin: 0;
  flex: 1;
  overflow-y: auto;
}
.pos-signer-item {
  background: #fff;
  border: 1px solid #e2e8f0;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.pos-signer-item:hover { border-color: #cbd5e1; }
.pos-signer-item.active {
  border-color: #2563eb;
  background: #eff6ff;
  box-shadow: 0 2px 4px rgba(37,99,235,0.1);
}
.pos-signer-item .sig-name { font-weight: 600; color: #1e293b; font-size: 0.9rem; }
.pos-signer-item .sig-role { font-size: 0.8rem; color: #64748b; }
.pos-signer-item .sig-status-ok { font-size: 0.75rem; color: #16a34a; margin-top: 4px; }
.pos-tips {
  margin-top: 20px;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-size: 0.8rem;
  color: #475569;
}
.pos-viewer {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #e2e8f0;
  position: relative;
  overflow: hidden;
}
.pdf-toolbar {
  padding: 10px 20px;
  background: #fff;
  border-bottom: 1px solid #cbd5e1;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  font-weight: 600;
  color: #334155;
}
.pdf-scroll-area {
  flex: 1;
  overflow: auto;
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}
.pdf-page-wrapper {
  position: relative;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  /* The size will be naturally dictated by VuePdfEmbed */
  display: inline-block;
}
.pos-actions {
  padding: 16px 24px;
  background: #fff;
  border-top: 1px solid #cbd5e1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pos-actions span { color: #475569; font-size: 0.9rem; }
.pos-actions .btn-primary { width: auto; }
.draggable-stamp {
  position: absolute;
  /* Fundo sutil para parecer com o gerador final */
  background: rgba(248, 250, 252, 0.95);
  border: 1px solid #94a3b8;
  border-radius: 4px;
  cursor: grab;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  backdrop-filter: blur(2px);
  z-index: 10;
  transition: box-shadow 0.2s, border-color 0.2s;
  user-select: none;
  overflow: hidden;
}
.draggable-stamp:active, .draggable-stamp.dragging { 
  cursor: grabbing; 
  box-shadow: 0 8px 16px rgba(37,99,235,0.25); 
  border-color: #2563eb;
}
.stamp-content { 
  display: flex;
  flex-direction: column;
  justify-content: center;
  pointer-events: none; 
  width: 100%; 
  padding: 4px 6px; 
  box-sizing: border-box; 
}
.stamp-content .s-by { font-size: 0.45rem; color: #64748b; font-style: italic; margin-bottom: 2px; }
.stamp-content .s-name { font-size: 0.75rem; color: #1e293b; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.1; }
.stamp-content .s-doc { font-size: 0.55rem; color: #475569; white-space: nowrap; margin-top: 1px; }
.color-red { color: #ef4444; }
.color-blue { color: #2563eb; }
.color-slate { color: #64748b; }

.badge-pdf { background: #fee2e2; color: #b91c1c; }
.badge-word { background: #dbeafe; color: #1e40af; }
.badge-generic { background: #f1f5f9; color: #475569; }
</style>
