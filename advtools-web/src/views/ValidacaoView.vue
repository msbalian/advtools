<template>
  <div class="validacao-page">
    <header class="public-nav">
      <div class="nav-brand">
        <i class="fas fa-pen-nib"></i>
        <span>ADVtools <strong>Sign</strong></span>
      </div>
      <div class="nav-badge">
        <i class="fas fa-shield-alt"></i> Validação Pública
      </div>
    </header>

    <div class="validacao-container" v-if="loaded">
      <div v-if="error" class="error-box">
        <i class="fas fa-times-circle"></i>
        <h2>Documento Não Encontrado</h2>
        <p>O código de validação não corresponde a nenhum documento registrado.</p>
      </div>

      <div v-else class="validation-card">
        <div class="validation-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <h2>Documento Autêntico</h2>
        <p class="validation-subtitle">Este documento foi assinado digitalmente via ADVtools Sign.</p>

        <div class="info-grid">
          <div class="info-item">
            <label>Documento</label>
            <span>{{ docData.nome }}</span>
          </div>
          <div class="info-item">
            <label>Status</label>
            <span class="status-badge">{{ docData.status_assinatura }}</span>
          </div>
          <div class="info-item">
            <label>Hash SHA-256 (Original)</label>
            <span class="hash-text">{{ docData.hash_original || 'Não disponível' }}</span>
          </div>
        </div>

        <div class="legal-footer">
          <p><i class="fas fa-gavel"></i> A validade jurídica deste documento é amparada pela Medida Provisória 2.200-2/2001 (ICP-Brasil).</p>
        </div>
      </div>
    </div>

    <div v-else class="loading-container">
      <i class="fas fa-spinner fa-spin"></i>
      <p>Verificando autenticidade...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const token = route.params.token as string
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const loaded = ref(false)
const error = ref(false)
const docData = ref<any>({})

async function validate() {
  try {
    const res = await fetch(`${API}/api/public/validar/${token}`)
    if (!res.ok) {
      error.value = true
    } else {
      docData.value = await res.json()
    }
  } catch (e) {
    error.value = true
  }
  loaded.value = true
}

onMounted(validate)
</script>

<style scoped>
.validacao-page {
  min-height: 100vh;
  background: #f0f4f8;
  font-family: 'Inter', sans-serif;
}

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

.validacao-container {
  max-width: 600px;
  margin: 60px auto;
  padding: 0 20px;
}

.error-box {
  text-align: center;
  background: #fff;
  border-radius: 16px;
  padding: 60px 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.error-box i { font-size: 3.5rem; color: #dc2626; }
.error-box h2 { color: #1e293b; margin-top: 15px; }
.error-box p { color: #64748b; }

.validation-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  text-align: center;
}
.validation-icon i {
  font-size: 4rem;
  color: #16a34a;
}
.validation-card h2 {
  color: #1e293b;
  margin: 15px 0 5px;
}
.validation-subtitle {
  color: #64748b;
  margin-bottom: 30px;
}

.info-grid {
  text-align: left;
  border-top: 1px solid #f1f5f9;
  padding-top: 20px;
}
.info-item {
  margin-bottom: 16px;
}
.info-item label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.info-item span {
  font-size: 0.95rem;
  color: #1e293b;
}
.status-badge {
  background: #dcfce7;
  color: #166534;
  padding: 3px 10px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.85rem;
}
.hash-text {
  font-family: monospace;
  font-size: 0.8rem !important;
  color: #64748b !important;
  word-break: break-all;
}

.legal-footer {
  margin-top: 30px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
}
.legal-footer p {
  font-size: 0.78rem;
  color: #64748b;
  margin: 0;
}
.legal-footer i { color: #94a3b8; margin-right: 5px; }

.loading-container {
  text-align: center;
  padding: 100px 20px;
  color: #64748b;
}
.loading-container i { font-size: 2rem; color: #2563eb; }
</style>
