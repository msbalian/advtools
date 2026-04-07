import { X, Check } from 'lucide-react';

export default function Comparison() {
    return (
        <section className="py-24 bg-white relative overflow-hidden">
            <div className="absolute top-0 right-0 w-[60%] h-full bg-slate-50/50 -skew-x-12 transform origin-top-right"></div>
            <div className="max-w-6xl mx-auto px-6 relative z-10">
                <div className="text-center mb-16">
                    <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6 tracking-tight">A conta fecha muito mais rápido</h2>
                    <p className="text-lg text-slate-500 max-w-2xl mx-auto leading-relaxed font-light">
                        Veja como um escritório geralmente se atrapalha e perde dinheiro contratando serviços pulverizados, ao invés de centralizar tudo numa única assinatura.
                    </p>
                </div>

                <div className="flex flex-col lg:flex-row gap-8 max-w-5xl mx-auto">
                    {/* Old Way */}
                    <div className="flex-1 bg-slate-50 p-8 md:p-10 rounded-[2rem] border border-slate-200 opacity-90">
                        <h3 className="text-2xl font-semibold text-slate-600 mb-8 border-b border-slate-200 pb-4">O jeito tradicional (pulverizado)</h3>
                        <ul className="space-y-6">
                            <li className="flex items-center justify-between text-slate-500">
                                <span className="flex items-center gap-3"><X className="w-5 h-5 text-red-400" /> Assinador Digital Externo</span>
                                <span className="font-mono opacity-60">R$ 50+/mês</span>
                            </li>
                            <li className="flex items-center justify-between text-slate-500">
                                <span className="flex items-center gap-3"><X className="w-5 h-5 text-red-400" /> CRM de Vendas</span>
                                <span className="font-mono opacity-60">R$ 150+/mês</span>
                            </li>
                            <li className="flex items-center justify-between text-slate-500">
                                <span className="flex items-center gap-3"><X className="w-5 h-5 text-red-400" /> Software de Gestão Limitado</span>
                                <span className="font-mono opacity-60 text-sm">(Depende da licença)</span>
                            </li>
                            <li className="flex items-center justify-between text-slate-500">
                                <span className="flex items-center gap-3"><X className="w-5 h-5 text-red-400" /> Gateway para Cartão/PIX</span>
                                <span className="font-mono opacity-60 text-sm">Taxas altíssimas</span>
                            </li>
                        </ul>
                        <div className="mt-10 pt-6 border-t border-slate-200 text-center text-slate-400 text-sm font-medium">
                            Gestão dispersa em múltiplas abas, dados isolados.
                        </div>
                    </div>

                    {/* ADVtools Way */}
                    <div className="flex-1 bg-brand-dark text-white p-8 md:p-10 rounded-[2rem] border border-brand shadow-2xl relative transform lg:-translate-y-4">
                        <div className="absolute top-0 right-10 transform -translate-y-1/2 bg-brand-light text-white px-5 py-1.5 rounded-full text-sm font-bold shadow-lg mt-0">
                            A Escolha Certa
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-8 border-b border-brand-light/30 pb-4">A Assinatura ADVtools</h3>
                        <ul className="space-y-6">
                            <li className="flex items-center justify-between text-blue-50 font-medium tracking-wide">
                                <span className="flex items-center gap-3"><Check className="w-5 h-5 text-green-400" /> Assinador Digital Integrado</span>
                            </li>
                            <li className="flex items-center justify-between text-blue-50 font-medium tracking-wide">
                                <span className="flex items-center gap-3"><Check className="w-5 h-5 text-green-400" /> CRM & Captação Integrados</span>
                            </li>
                            <li className="flex items-center justify-between text-blue-50 font-medium tracking-wide">
                                <span className="flex items-center gap-3"><Check className="w-5 h-5 text-green-400" /> Gestão Processual & Documentos</span>
                            </li>
                            <li className="flex items-center justify-between text-blue-50 font-medium tracking-wide">
                                <span className="flex items-center gap-3"><Check className="w-5 h-5 text-green-400" /> Módulo Fincanceiro & Pagamentos</span>
                            </li>
                        </ul>
                        <div className="mt-10 pt-6 border-t border-brand-light/30 text-center">
                            <span className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-blue-200">Tudo Centralizado</span>
                            <p className="text-brand-light mt-2 font-medium">Em uma interface premium e rápida</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
