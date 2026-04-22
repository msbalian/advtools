<script setup lang="ts">
import { 
  Cpu, 
  Signature, 
  FileSearch, 
  Database, 
  Zap, 
  CreditCard, 
  Calendar,
  Layers,
  FileText,
  CheckCircle2,
  ArrowRight
} from 'lucide-vue-next';

const currentFeatures = [
  {
    title: 'ADVtools Sign',
    icon: Signature,
    description: 'Módulo de assinatura eletrônica nativo com biometria e auditoria completa.',
    specs: [
      'Autenticação via Biometria Facial (WebRTC)',
      'Assinatura Digital em Canvas (Touch/Mouse)',
      'Tokenização de links com UUIDv4',
      'Certificados de Auditoria com QR Code dinâmico',
      'Validação pública de integridade via hash SHA256'
    ]
  },
  {
    title: 'Smart Monitor',
    icon: FileSearch,
    description: 'Monitoramento judicial inteligente e automatizado.',
    specs: [
      'Discovery via OAB e CPF (DataJud integration)',
      'Sincronização MNI/Projudi em tempo real',
      'Motor de verificação em background 24/7',
      'Extração automatizada de movimentações',
      'Alertas de prazos baseados em publicações'
    ]
  },
  {
    title: 'Redator de I.A.',
    icon: Cpu,
    description: 'Geração de conteúdo jurídico assistida por Inteligência Artificial.',
    specs: [
      'Modelos (templates) inteligentes e dinâmicos',
      'Geração de petições baseada no histórico do processo',
      'IA treinada em jurisprudência atualizada',
      'Corretor gramatical e jurídico integrado',
      'Sincronização com o editor de texto nativo'
    ]
  },
  {
    title: 'Infraestrutura Core',
    icon: Database,
    description: 'Arquitetura resiliente e segura para grandes escritórios.',
    specs: [
      'Multi-tenancy com isolamento de dados',
      'Armazenamento redundante (Storage Audit)',
      'Barramento de eventos para sincronização assíncrona',
      'API RESTful robusta com autenticação JWT',
      'Database schema otimizado para performance em escala'
    ]
  }
];

const roadmapFeatures = [
  {
    title: 'Agenda & Controle de Tarefas',
    icon: Calendar,
    status: 'Em Desenvolvimento',
    description: 'Gestão completa de cronograma e delegação de tarefas por equipe.',
    details: 'Integração com Google Calendar e Outlook, visões Kanban e Gantt.'
  },
  {
    title: 'Financeiro Integrado',
    icon: CreditCard,
    status: 'Em Desenvolvimento',
    description: 'Gateways EFI e Stripe para automação de cobranças.',
    details: 'Emissão de boletos, PIX e cartões com conciliação bancária automática.'
  },
  {
    title: 'Organizador Inteligente',
    icon: Layers,
    status: 'Em Planejamento',
    description: 'IA para separação e protocolo de documentos.',
    details: 'Classificação automática de anexos para peticionamento massificado.'
  },
  {
    title: 'Petições Escritas via IA',
    icon: FileText,
    status: 'Em Planejamento',
    description: 'Prazos e sugestões de petições sugeridas pela IA.',
    details: 'A IA analisa a movimentação e sugere a resposta jurídica imediata.'
  }
];
</script>

<template>
  <div class="min-h-screen bg-[#020617] text-slate-200 font-sans antialiased overflow-x-hidden">
    <!-- Header/Hero -->
    <header class="relative pt-20 pb-32 px-6">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_50%_-20%,rgba(12,149,235,0.15),transparent)] pointer-events-none"></div>
      <div class="max-w-6xl mx-auto text-center relative z-10">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-8">
          <Zap class="w-4 h-4" />
          <span>Especificações Técnicas & Roadmap</span>
        </div>
        <h1 class="text-5xl md:text-7xl font-bold tracking-tighter text-white mb-6">
          A Engenharia do <span class="text-blue-500">Amanhã</span> no Direito.
        </h1>
        <p class="text-xl text-slate-400 max-w-3xl mx-auto leading-relaxed">
          O ADVtools não é apenas um software de gestão; é um ecossistema técnico robusto construído para performance, segurança e automação real via IA.
        </p>
      </div>
    </header>

    <!-- Specs Grid -->
    <section class="max-w-7xl mx-auto px-6 pb-32">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div 
          v-for="feature in currentFeatures" 
          :key="feature.title"
          class="group bg-slate-900/50 border border-slate-800 p-8 rounded-sm hover:border-blue-500/50 transition-all duration-300 relative overflow-hidden"
        >
          <div class="absolute -right-4 -top-4 opacity-[0.03] group-hover:opacity-[0.08] group-hover:scale-110 transition-all duration-500">
            <component :is="feature.icon" class="w-48 h-48" />
          </div>
          
          <div class="flex items-start gap-4 mb-6">
            <div class="p-3 bg-blue-500/10 rounded-sm text-blue-400">
              <component :is="feature.icon" class="w-6 h-6" />
            </div>
            <div>
              <h3 class="text-2xl font-bold text-white tracking-tight">{{ feature.title }}</h3>
              <p class="text-slate-500 mt-1">{{ feature.description }}</p>
            </div>
          </div>

          <ul class="space-y-3">
            <li v-for="spec in feature.specs" :key="spec" class="flex items-center gap-3 text-sm text-slate-400">
              <CheckCircle2 class="w-4 h-4 text-emerald-500/70 shrink-0" />
              {{ spec }}
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Roadmap Vertical Stream -->
    <section class="bg-slate-900/30 border-y border-slate-800 py-32 px-6">
      <div class="max-w-4xl mx-auto">
        <div class="text-center mb-20">
          <h2 class="text-4xl font-bold text-white mb-4">Próximos Passos</h2>
          <p class="text-slate-500">Recursos em desenvolvimento ativo que redefinirão a operação jurídica.</p>
        </div>

        <div class="space-y-12">
          <div 
            v-for="(item, index) in roadmapFeatures" 
            :key="item.title"
            class="flex flex-col md:flex-row gap-8 relative"
          >
            <!-- Timeline Line -->
            <div v-if="index !== roadmapFeatures.length - 1" class="hidden md:block absolute left-[31px] top-16 bottom-[-32px] w-[2px] bg-gradient-to-b from-blue-500/30 to-transparent"></div>

            <div class="flex-shrink-0 z-10">
              <div class="w-16 h-16 rounded-sm bg-slate-800 border border-slate-700 flex items-center justify-center text-blue-400 group-hover:text-blue-300 transition-colors">
                <component :is="item.icon" class="w-8 h-8" />
              </div>
            </div>

            <div class="flex-grow pt-2">
              <div class="flex items-center gap-3 mb-2">
                <span class="text-xs font-bold uppercase tracking-widest text-blue-500/80">{{ item.status }}</span>
                <div class="h-[1px] flex-grow bg-slate-800"></div>
              </div>
              <h3 class="text-2xl font-bold text-white mb-2">{{ item.title }}</h3>
              <p class="text-slate-400 mb-4">{{ item.description }}</p>
              <div class="p-4 bg-slate-900 border-l-2 border-blue-500 text-sm text-slate-500 italic">
                {{ item.details }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer CTA -->
    <footer class="py-32 px-6 text-center">
      <div class="max-w-2xl mx-auto">
        <h2 class="text-3xl font-bold text-white mb-8">Pronto para elevar o nível técnico do seu escritório?</h2>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <router-link to="/register" class="w-full sm:w-auto px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-sm transition-all flex items-center justify-center gap-2">
            Iniciar Trial Gratuito
            <ArrowRight class="w-5 h-5" />
          </router-link>
          <router-link to="/" class="w-full sm:w-auto px-8 py-4 bg-transparent border border-slate-700 hover:border-slate-500 text-white font-bold rounded-sm transition-all">
            Falar com Consultor
          </router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Design Blueprint Theme overrides */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

.font-mono {
  font-family: 'JetBrains Mono', monospace;
}

/* Sharp lines, technical feel */
:deep(.rounded-sm), .rounded-sm {
  border-radius: 2px !important;
}

/* Custom transitions */
.feature-card-enter-active {
  transition: all 0.5s ease;
}
.feature-card-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
</style>
