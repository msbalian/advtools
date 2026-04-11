<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentYear = computed(() => new Date().getFullYear())

const email = ref('')
const message = ref('')
const errorMsg = ref('')
const isLoading = ref(false)
const isSuccess = ref(false)

const handleForgotPassword = async () => {
  isLoading.value = true
  errorMsg.value = ''
  message.value = ''
  
  try {
    const response = await fetch('/api/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value })
    })

    const data = await response.json()
    
    if (!response.ok) {
       throw new Error(data.detail || 'Erro ao solicitar recuperação de senha.')
    }

    isSuccess.value = true
    message.value = data.message || 'Se o e-mail estiver cadastrado, as instruções foram enviadas.'
    
  } catch (err) {
    errorMsg.value = err.message || 'Erro de conexão com o servidor.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-slate-50">
    <main class="flex-grow flex items-center justify-center p-4">
      <div class="card w-full max-w-md p-8 sm:p-10 space-y-8 animate-fade-in-up">
        
        <!-- Logo / Branding -->
        <div class="text-center space-y-4 flex flex-col items-center">
          <img src="../assets/logo-horizontal.png" alt="ADVtools Logo" class="h-20 object-contain transform transition hover:scale-105" />
          <h2 class="text-2xl font-bold text-slate-900">Recuperar Senha</h2>
          <p class="text-slate-500 text-sm">Insira seu e-mail para receber um link de redefinição.</p>
        </div>

        <div v-if="isSuccess" class="space-y-6">
          <div class="p-4 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg text-sm font-medium animate-fade-in-up">
            {{ message }}
          </div>
          <button @click="router.push('/')" class="btn-primary w-full flex justify-center py-2.5">
            Voltar para o Login
          </button>
        </div>

        <!-- Form -->
        <form v-else class="space-y-6" @submit.prevent="handleForgotPassword">
          
          <div v-if="errorMsg" class="p-3 bg-red-50 text-red-600 border border-red-200 rounded-lg text-sm font-medium animate-fade-in-up">
            {{ errorMsg }}
          </div>
          
          <div>
            <label for="email" class="block text-sm font-semibold leading-6 text-slate-900">Email</label>
            <div class="mt-2">
              <input id="email" v-model="email" name="email" type="email" autocomplete="email" required class="input-field" placeholder="advogado@escritorio.com.br" />
            </div>
          </div>

          <div class="space-y-4">
            <button type="submit" :disabled="isLoading" class="btn-primary w-full flex justify-center py-2.5 disabled:opacity-75">
              {{ isLoading ? 'Enviando...' : 'Enviar Link de Recuperação' }}
            </button>
            <button type="button" @click="router.push('/')" class="text-sm font-semibold text-slate-500 hover:text-slate-700 w-full text-center transition-colors">
              Voltar para o login
            </button>
          </div>
        </form>
      </div>
    </main>

    <footer class="py-6 text-center">
      <p class="text-sm text-slate-400">
        &copy; {{ currentYear }} ADVtools. Todos os direitos reservados.
      </p>
    </footer>
  </div>
</template>
