import { createRouter, createWebHistory } from 'vue-router'
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'login',
            component: LoginView
        },
        {
            path: '/register',
            name: 'register',
            component: () => import('./views/RegisterView.vue')
        },
        {
            path: '/dashboard',
            name: 'dashboard',
            component: DashboardView,
            meta: { requiresAuth: true }
        },
        {
            path: '/clientes',
            name: 'clientes',
            component: () => import('./views/ClientesView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/clientes/:id',
            name: 'cliente_detalhes',
            component: () => import('./views/ClienteDetalhesView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/servicos',
            name: 'servicos',
            component: () => import('./views/ServicosView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/modelos',
            name: 'modelos',
            component: () => import('./views/DocsEscritorioView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/configuracoes',
            name: 'configuracoes',
            component: () => import('./views/ConfiguracoesView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/redator',
            name: 'redator',
            component: () => import('./views/RedatorView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/processos',
            name: 'processos',
            component: () => import('./views/ProcessosView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/tarefas',
            name: 'tarefas',
            component: () => import('./views/TarefasView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/financeiro',
            name: 'financeiro',
            component: () => import('./views/FinanceiroView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/arquivos',
            name: 'arquivos',
            component: () => import('./views/ArquivosView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/processos/:id',
            name: 'processo_detalhes',
            component: () => import('./views/ProcessoDetalheView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/documentos/:id/assinaturas',
            name: 'gerenciar_assinaturas',
            component: () => import('./views/AssinaturasGerenciarView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/admin/usuarios',
            name: 'admin_usuarios',
            component: () => import('./views/SuperAdminUsersView.vue'),
            meta: { requiresAuth: true }
        },
        // === ROTAS PÚBLICAS (sem autenticação) ===
        {
            path: '/assinar/:token',
            name: 'sala_assinatura',
            component: () => import('./views/SalaAssinaturaView.vue'),
            meta: { requiresAuth: false, publicRoute: true }
        },
        {
            path: '/validar/:token',
            name: 'validacao_assinatura',
            component: () => import('./views/ValidacaoView.vue'),
            meta: { requiresAuth: false, publicRoute: true }
        }
    ]
})

// Global navigation guard for authentication
router.beforeEach((to, _from) => {
    const isAuthenticated = !!localStorage.getItem('advtools_token')

    // Public routes bypass all auth logic
    if (to.matched.some(record => record.meta.publicRoute)) {
        return true
    }

    // Check if the route requires authentication
    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!isAuthenticated) {
            return { name: 'login' }
        }
        return true
    }

    // Non-auth routes (login/register): redirect to app if already logged in
    if (isAuthenticated && (to.name === 'login' || to.name === 'register')) {
        return { name: 'clientes' }
    }

    return true
})

export default router

