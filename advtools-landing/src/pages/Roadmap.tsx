import {
    Zap,
    Cpu,
    Signature,
    FileSearch,
    Database,
    CreditCard,
    Calendar,
    Layers,
    FileText,
    CheckCircle2,
    ArrowRight
} from 'lucide-react';
import { Link } from 'react-router-dom';

const technicalModules = [
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
    },
    {
        title: 'Agenda & Controle de Tarefas',
        icon: Calendar,
        description: 'Gestão completa de cronograma e delegação de tarefas por equipe.',
        specs: [
            'Integração com Google Calendar e Outlook',
            'Visões Kanban e Gantt para fluxos internos',
            'Notificações push e e-mail para prazos fatais',
            'Delegação inteligente baseada em carga de trabalho'
        ]
    },
    {
        title: 'Controladoria Financeira',
        icon: CreditCard,
        tag: 'Em Breve',
        description: 'Automação total de faturamento e conciliação.',
        specs: [
            'Gateways EFI e Stripe integrados nativamente',
            'Emissão de Boletos e PIX com retorno em tempo real',
            'Gestão de honorários e despesas processuais',
            'Relatórios de DRE e fluxo de caixa automático'
        ]
    },
    {
        title: 'Organizador de Documentos',
        icon: Layers,
        tag: 'Em Breve',
        description: 'IA para separação e protocolo de documentos.',
        specs: [
            'Classificação automática de anexos (OCR/IA)',
            'Baseado em IA para separação por tipo de documento',
            'Preparação inteligente para protocolo massificado',
            'Extração de metadados de arquivos escaneados'
        ]
    },
    {
        title: 'Assistente Jurídico IA+',
        icon: FileText,
        description: 'Sugestões proativas de resposta jurídica.',
        specs: [
            'Análise de movimentação em tempo real',
            'Sugestão automática da petição de resposta',
            'Identificação de prazos e preenchimento de agenda',
            'Histórico de teses vencedoras para referência'
        ]
    }
];

export default function Roadmap() {
    return (
        <div className="min-h-screen bg-[#020617] text-slate-200 font-sans antialiased overflow-x-hidden">
            {/* Header/Hero */}
            <header className="relative pt-20 pb-32 px-6">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_-20%,rgba(12,149,235,0.15),transparent)] pointer-events-none"></div>
                <div className="max-w-6xl mx-auto text-center relative z-10">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-8">
                        <Zap className="w-4 h-4" />
                        <span>Arquitetura Técnica & Ecossistema</span>
                    </div>
                    <h1 className="text-5xl md:text-7xl font-bold tracking-tighter text-white mb-6">
                        A Engenharia do <span className="text-blue-500">Amanhã</span> no Direito.
                    </h1>
                    <p className="text-xl text-slate-400 max-w-3xl mx-auto leading-relaxed font-light">
                        O ADVtools não é apenas um software de gestão; é um ecossistema técnico robusto construído para performance, segurança e automação real via IA.
                    </p>
                </div>
            </header>

            {/* Specs Grid */}
            <section className="max-w-7xl mx-auto px-6 pb-40">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {technicalModules.map((feature) => (
                        <div
                            key={feature.title}
                            className="group bg-slate-900/50 border border-slate-800 p-8 rounded-[2px] hover:border-blue-500/50 transition-all duration-300 relative overflow-hidden flex flex-col h-full"
                        >
                            <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:opacity-[0.08] group-hover:scale-110 transition-all duration-500 pointer-events-none">
                                <feature.icon size={192} />
                            </div>

                            <div className="flex items-start justify-between mb-6">
                                <div className="p-3 bg-blue-500/10 rounded-[2px] text-blue-400">
                                    <feature.icon size={24} />
                                </div>
                                {feature.tag && (
                                    <span className="px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-[10px] uppercase font-bold tracking-widest">
                                        {feature.tag}
                                    </span>
                                )}
                            </div>

                            <div className="mb-6">
                                <h3 className="text-2xl font-bold text-white tracking-tight">{feature.title}</h3>
                                <p className="text-slate-500 mt-1 text-sm leading-relaxed">{feature.description}</p>
                            </div>

                            <ul className="space-y-3 mt-auto">
                                {feature.specs.map((spec) => (
                                    <li key={spec} className="flex items-center gap-3 text-sm text-slate-400">
                                        <CheckCircle2 size={16} className="text-emerald-500/70 shrink-0" />
                                        {spec}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            </section>

            {/* Footer CTA */}
            <footer className="py-32 px-6 text-center">
                <div className="max-w-2xl mx-auto text-center flex flex-col items-center">
                    <h2 className="text-3xl font-bold text-white mb-8">Pronto para elevar o nível técnico do seu escritório?</h2>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full">
                        <Link to="/" className="w-full sm:w-auto px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-[2px] transition-all flex items-center justify-center gap-2">
                            Iniciar Trial Gratuito
                            <ArrowRight size={20} />
                        </Link>
                        <Link to="/" className="w-full sm:w-auto px-8 py-4 bg-transparent border border-slate-700 hover:border-slate-500 text-white font-bold rounded-[2px] transition-all">
                            Falar com Consultor
                        </Link>
                    </div>
                </div>
            </footer>
        </div>
    );
}
