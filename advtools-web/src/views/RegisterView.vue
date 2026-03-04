<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { vMaska } from 'maska/vue'

const router = useRouter()
const currentYear = computed(() => new Date().getFullYear())

const form = ref({
  nome_escritorio: '',
  documento_escritorio: '',
  nome_usuario: '',
  email: '',
  senha: '',
  confirmar_senha: ''
})

const errorMsg = ref('')
const successMsg = ref('')
const isLoading = ref(false)

const handleRegister = async () => {
  if (form.value.senha !== form.value.confirmar_senha) {
    errorMsg.value = 'As senhas não coincidem.'
    return
  }

  isLoading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  
  try {
    // 1. Criar o Escritório primeiro (Simulado via API composta ou podemos ajustar no backend depois)
    // Para simplificar, vamos assumir que o backend de /register espera os dados unificados
    // ou cria um escritório default. No nosso schema atual UsuarioCreate pede escritorio_id.
    // Como estamos num "Big Bang", precisaremos ajustar a API de register para aceitar os dados do escritório também.
    // Vamos enviar os dados adicionais no body e ajustar o backend em seguida se necessário.
    
    // Por enquanto, vamos consumir um endpoint customizado ou ajustar o que criamos.
    // O ideal: criar escritório -> pegar ID -> criar usuário. Vamos tentar fazer as duas chamadas se a API permitir POST /escritorios pública.
    
    // Workaround temporário: vamos focar no visual e conectar chamadas simples:
    const resEscritorio = await fetch('/api/escritorios', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nome: form.value.nome_escritorio,
        documento: form.value.documento_escritorio
      })
    })

    if (!resEscritorio.ok) throw new Error('Erro ao registrar escritório')
    const escritorio = await resEscritorio.json()

    // 2. Criar o Usuário vinculado
    const resAuth = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nome: form.value.nome_usuario,
        email: form.value.email,
        senha: form.value.senha,
        escritorio_id: escritorio.id,
        is_admin: false, // O primeiro usuário do escritório é ADMIN DO ESCRITÓRIO, não SuperAdmin global
        perfil: 'Admin'
      })
    })

    if (!resAuth.ok) {
       const resData = await resAuth.json()
       throw new Error(resData.detail || 'Erro ao registrar usuário')
    }

    // 3. Fazer Login Automaticamente
    const loginFormData = new FormData()
    loginFormData.append('username', form.value.email)
    loginFormData.append('password', form.value.senha)

    const resLogin = await fetch('/api/login', {
      method: 'POST',
      body: loginFormData
    })

    if (resLogin.ok) {
        const loginData = await resLogin.json()
        localStorage.setItem('advtools_token', loginData.access_token)
        successMsg.value = 'Conta criada com sucesso! Redirecionando para o painel...'
        setTimeout(() => {
           router.push('/dashboard')
        }, 1500)
    } else {
        successMsg.value = 'Conta criada com sucesso! Redirecionando para login...'
        setTimeout(() => {
           router.push('/')
        }, 2000)
    }
    
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
      <!-- Register Card -->
      <div class="card w-full max-w-xl p-8 sm:p-10 space-y-8 animate-fade-in-up">
        
        <!-- Logo -->
        <div class="text-center space-y-4 flex flex-col items-center">
          <img src="../assets/logo-horizontal.png" alt="ADVtools Logo" class="h-16 object-contain transform transition hover:scale-105" />
          <h2 class="text-2xl font-bold tracking-tight text-slate-900">Crie sua conta ADVtools</h2>
          <p class="text-sm text-slate-500">Comece a gerenciar seu escritório de forma inteligente.</p>
        </div>

        <!-- Form -->
        <form class="space-y-6" @submit.prevent="handleRegister">
          
          <div v-if="errorMsg" class="p-3 bg-red-50 text-red-600 border border-red-200 rounded-lg text-sm font-medium animate-fade-in-up">
            {{ errorMsg }}
          </div>
          
          <div v-if="successMsg" class="p-3 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg text-sm font-medium animate-fade-in-up">
            {{ successMsg }}
          </div>

          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
             <!-- Seção Escritório -->
             <div class="sm:col-span-2 border-b border-slate-100 pb-2">
                <h3 class="text-sm font-semibold text-slate-800">Dados do Escritório</h3>
             </div>
             
             <div class="sm:col-span-2">
               <label class="block text-sm font-medium leading-6 text-slate-900">Nome do Escritório *</label>
               <input v-model="form.nome_escritorio" type="text" required class="mt-2 input-field" placeholder="Ex: Silva & Advogados Associados" />
             </div>
             
             <div class="sm:col-span-2">
               <label class="block text-sm font-medium leading-6 text-slate-900">CNPJ / CPF do Titular</label>
               <input v-model="form.documento_escritorio" v-maska data-maska="['###.###.###-##', '##.###.###/####-##']" type="text" class="mt-2 input-field" placeholder="00.000.000/0000-00" />
             </div>

             <!-- Seção Usuário -->
             <div class="sm:col-span-2 border-b border-slate-100 pb-2 mt-4">
                <h3 class="text-sm font-semibold text-slate-800">Seu Perfil de Acesso</h3>
             </div>

             <div class="sm:col-span-2">
               <label class="block text-sm font-medium leading-6 text-slate-900">Seu Nome Completo *</label>
               <input v-model="form.nome_usuario" type="text" required class="mt-2 input-field" placeholder="João da Silva" />
             </div>
             
             <div class="sm:col-span-2">
               <label class="block text-sm font-medium leading-6 text-slate-900">Email (Acesso) *</label>
               <input v-model="form.email" type="email" autocomplete="email" required class="mt-2 input-field" placeholder="joao@escritorio.com.br" />
             </div>

             <div>
               <label class="block text-sm font-medium leading-6 text-slate-900">Senha *</label>
               <input v-model="form.senha" type="password" required class="mt-2 input-field" placeholder="••••••••" />
             </div>

             <div>
               <label class="block text-sm font-medium leading-6 text-slate-900">Confirmar Senha *</label>
               <input v-model="form.confirmar_senha" type="password" required class="mt-2 input-field" placeholder="••••••••" />
             </div>
          </div>

          <div class="pt-4">
            <button type="submit" :disabled="isLoading" class="btn-primary w-full flex justify-center py-3 text-base shadow-primary-500/40 disabled:opacity-75">
              {{ isLoading ? 'Criando Conta...' : 'Começar a Usar o ADVtools' }}
            </button>
          </div>
        </form>

        <!-- Footer link -->
        <p class="mt-10 text-center text-sm text-slate-500">
          Já possui uma conta?
          {{ ' ' }}
          <router-link to="/" class="font-semibold leading-6 text-primary-600 hover:text-primary-500 transition-colors">Faça login aqui</router-link>
        </p>
      </div>
    </main>

    <!-- Footer -->
    <footer class="py-6 text-center">
      <p class="text-sm text-slate-400">
        &copy; {{ currentYear }} ADVtools. Todos os direitos reservados.
      </p>
    </footer>
  </div>
</template>
