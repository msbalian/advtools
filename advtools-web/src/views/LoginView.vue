<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentYear = computed(() => new Date().getFullYear())

const email = ref('fernando@primejud.com.br')
const password = ref('123')
const errorMsg = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  isLoading.value = true
  errorMsg.value = ''
  
  try {
    const formData = new URLSearchParams()
    formData.append('username', email.value)
    formData.append('password', password.value)

    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })

    if (!response.ok) {
       throw new Error('E-mail ou senha incorretos.')
    }

    const data = await response.json()
    localStorage.setItem('advtools_token', data.access_token)
    router.push('/dashboard')
    
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
      <!-- Login Card Start -->
      <div class="card w-full max-w-md p-8 sm:p-10 space-y-8 animate-fade-in-up">
        
        <!-- Logo / Branding -->
        <div class="text-center space-y-4 flex flex-col items-center">
          <img src="../assets/logo-horizontal.png" alt="ADVtools Logo" class="h-20 object-contain transform transition hover:scale-105" />
        </div>

        <!-- Form -->
        <form class="space-y-6" @submit.prevent="handleLogin">
          
          <div v-if="errorMsg" class="p-3 bg-red-50 text-red-600 border border-red-200 rounded-lg text-sm font-medium animate-fade-in-up">
            {{ errorMsg }}
          </div>
          
          <div>
            <label for="email" class="block text-sm font-semibold leading-6 text-slate-900">Email</label>
            <div class="mt-2">
              <input id="email" v-model="email" name="email" type="email" autocomplete="email" required class="input-field" placeholder="advogado@escritorio.com.br" />
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between">
               <label for="password" class="block text-sm font-semibold leading-6 text-slate-900">Senha</label>
               <div class="text-sm">
                 <a href="#" class="font-semibold text-primary-600 hover:text-primary-500 transition-colors">Esqueceu a senha?</a>
               </div>
            </div>
            <div class="mt-2">
               <input id="password" v-model="password" name="password" type="password" autocomplete="current-password" required class="input-field" placeholder="••••••••" />
            </div>
          </div>

          <div>
            <button type="submit" :disabled="isLoading" class="btn-primary w-full flex justify-center py-2.5 disabled:opacity-75">
              {{ isLoading ? 'Autenticando...' : 'Entrar no Sistema' }}
            </button>
          </div>
        </form>

        <!-- Footer link -->
        <p class="mt-10 text-center text-sm text-slate-500">
          Ainda não tem acesso?
          {{ ' ' }}
          <router-link to="/register" class="font-semibold leading-6 text-primary-600 hover:text-primary-500 transition-colors">Crie uma conta para seu escritório</router-link>
        </p>
      </div>
      <!-- Login Card End -->
    </main>

    <!-- Footer Corporate -->
    <footer class="py-6 text-center">
      <p class="text-sm text-slate-400">
        &copy; {{ currentYear }} ADVtools. Todos os direitos reservados.
      </p>
    </footer>
  </div>
</template>
