import { ArrowRight, CheckCircle } from 'lucide-react';
import { getWhatsAppLink } from '../utils/whatsapp';

export default function Hero() {
    const waLink = getWhatsAppLink('62981229004', 'Olá! Gostaria de falar com um consultor sobre como o ADVtools pode colocar meu escritório no próximo nível.');

    return (
        <section className="relative overflow-hidden bg-slate-900 pt-32 pb-24 md:pt-40 md:pb-32">
            {/* Dynamic Background Gradients */}
            <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-brand opacity-30 rounded-full blur-[120px]"></div>
            <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-brand-light opacity-20 rounded-full blur-[120px]"></div>

            <div className="max-w-6xl mx-auto px-6 relative z-10 text-center flex flex-col items-center">
                <img src="/logo-horizontal-white.png" alt="ADVtools Logo" className="h-20 md:h-28 w-auto object-contain mb-12" />

                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8 backdrop-blur-md text-sm font-medium text-blue-200">
                    <span className="flex h-2 w-2 rounded-full bg-green-400"></span>
                    A melhor plataforma para o advogado moderno
                </div>

                <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 text-white leading-tight">
                    Tudo que o seu escritório precisa,<br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-300 to-brand-light">
                        em uma única plataforma.
                    </span>
                </h1>

                <p className="text-lg md:text-xl text-slate-300 max-w-2xl mx-auto mb-12 font-light leading-relaxed">
                    Reduza custos desenfreados, simplifique sua gestão diária e coloque o seu escritório em pé de igualdade com as maiores bancas usando o ADVtools.
                </p>

                <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
                    <a
                        href={waLink}
                        target="_blank"
                        rel="noreferrer"
                        className="group flex items-center justify-center gap-2 bg-brand-light text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-brand transition-all shadow-[0_0_40px_rgba(76,130,255,0.4)] hover:scale-105 w-full sm:w-auto"
                    >
                        Falar com Consultor
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </a>
                    <a
                        href="/roadmap"
                        className="flex items-center justify-center gap-2 bg-white/5 border border-white/10 text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-white/10 transition-all w-full sm:w-auto"
                    >
                        Especificações Técnicas
                    </a>
                </div>

                <div className="mt-14 flex flex-wrap justify-center gap-8 text-slate-400 text-sm font-medium">
                    <span className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-brand-light" /> Zero complicação</span>
                    <span className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-brand-light" /> Migração assistida</span>
                    <span className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-brand-light" /> Suporte premium</span>
                </div>
            </div>
        </section>
    );
}
