<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const currentYear = computed(() => new Date().getFullYear())

const token = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const isLoading = ref(false)
const isSuccess = ref(false)

onMounted(() => {
  // Pega o token da query string (URL)
  token.value = route.query.token || ''
  if (!token.value) {
    errorMsg.value = 'Token de recuperação não encontrado. Por favor, solicite um novo link.'
  }
})

const handleResetPassword = async () => {
  if (password.value !== confirmPassword.value) {
    errorMsg.value = 'As senhas não coincidem.'
    return
  }

  if (password.value.length < 6) {
    errorMsg.value = 'A senha deve ter pelo menos 6 caracteres.'
    return
  }

  isLoading.value = true
  errorMsg.value = ''
  
  try {
    const response = await fetch('/api/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        token: token.value,
        new_password: password.value 
      })
    })

    const data = await response.json()
    
    if (!response.ok) {
       throw new Error(data.detail || 'Erro ao redefinir senha.')
    }

    isSuccess.value = true
    successMsg.value = data.message || 'Sua senha foi alterada com sucesso!'
    
    // Redireciona para o login após 3 segundos
    setTimeout(() => {
      router.push('/')
    }, 3000)
    
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
          <h2 class="text-2xl font-bold text-slate-900">Nova Senha</h2>
          <p class="text-slate-500 text-sm">Crie uma nova senha segura para sua conta.</p>
        </div>

        <div v-if="isSuccess" class="space-y-6">
          <div class="p-4 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg text-sm font-medium animate-fade-in-up">
            {{ successMsg }}
          </div>
          <p class="text-center text-slate-500 text-sm animate-pulse">Redirecionando para o login em instantes...</p>
        </div>

        <!-- Form -->
        <form v-else class="space-y-6" @submit.prevent="handleResetPassword">
          
          <div v-if="errorMsg" class="p-3 bg-red-50 text-red-600 border border-red-200 rounded-lg text-sm font-medium animate-fade-in-up">
            {{ errorMsg }}
          </div>
          
          <div>
            <label for="password" class="block text-sm font-semibold leading-6 text-slate-900">Nova Senha</label>
            <div class="mt-2">
              <input id="password" v-model="password" name="password" type="password" required class="input-field" placeholder="••••••••" />
            </div>
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-semibold leading-6 text-slate-900">Confirmar Nova Senha</label>
            <div class="mt-2">
              <input id="confirmPassword" v-model="confirmPassword" name="confirmPassword" type="password" required class="input-field" placeholder="••••••••" />
            </div>
          </div>

          <div class="space-y-4">
            <button type="submit" :disabled="isLoading || !token" class="btn-primary w-full flex justify-center py-2.5 disabled:opacity-75">
              {{ isLoading ? 'Alterando...' : 'Redefinir Senha' }}
            </button>
            <button type="button" @click="router.push('/')" class="text-sm font-semibold text-slate-500 hover:text-slate-700 w-full text-center transition-colors">
              Cancelar e voltar ao login
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
