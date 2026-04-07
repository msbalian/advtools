import { PenTool, CreditCard, LayoutDashboard, Bot, Scale, ShieldCheck } from 'lucide-react';

const features = [
    { icon: PenTool, title: 'Assinador Digital Próprio', desc: 'Assinaturas com validade jurídica, QR Code e prova de vida sem pagar plataformas terceiras.' },
    { icon: CreditCard, title: 'Integração Financeira', desc: 'Gateway de pagamento integrado com PIX, boletos e conciliação bancária automática.' },
    { icon: LayoutDashboard, title: 'CRM Avançado', desc: 'Esteira de vendas completa. Acompanhe leads, clientes e assinaturas de contratos.' },
    { icon: Bot, title: 'Robôs de Automação', desc: 'Automatize tarefas maçantes, agende cobranças e deixe a tecnologia trabalhar por você.' },
    { icon: Scale, title: 'Processos', desc: 'Painel inteligente para lidar com as audiências e não perder andamentos importantes.' },
    { icon: ShieldCheck, title: 'Alta Segurança', desc: 'Seus dados e dos seus clientes criptografados e hospedados com padrões rigorosos (LGPD).' },
];

export default function Features() {
    return (
        <section className="py-24 bg-slate-50">
            <div className="max-w-6xl mx-auto px-6">
                <div className="text-center mb-16">
                    <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6 tracking-tight">Um ecossistema completo</h2>
                    <p className="text-lg text-slate-500 max-w-2xl mx-auto leading-relaxed">
                        Para que contratar cinco ferramentas diferentes, lidar com senhas separadas e faturas altíssimas, se o ADVtools entrega tudo nativamente?
                    </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((feat, idx) => (
                        <div
                            key={idx}
                            className="group p-8 rounded-[2rem] bg-white border border-slate-200 hover:border-brand-light/40 hover:shadow-2xl hover:shadow-brand/5 transition-all duration-300 hover:-translate-y-1"
                        >
                            <div className="w-14 h-14 rounded-2xl bg-slate-50 border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex items-center justify-center mb-6 group-hover:bg-brand-light group-hover:text-white group-hover:border-brand-light transition-colors text-brand">
                                <feat.icon className="w-7 h-7" />
                            </div>
                            <h3 className="text-xl font-bold text-slate-900 mb-3">{feat.title}</h3>
                            <p className="text-slate-500 leading-relaxed font-light">{feat.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
