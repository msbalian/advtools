import { MessageCircle } from 'lucide-react';
import { getWhatsAppLink } from '../utils/whatsapp';

export default function FinalCTA() {
    const waLink = getWhatsAppLink('62981229004', 'Olá! Gostaria de entender mais detalhadamente as soluções do ADVtools para o meu escritório.');

    return (
        <section className="py-24 bg-brand relative overflow-hidden">
            <div className="absolute top-[-50%] right-[-10%] w-[80%] h-[150%] bg-brand-light opacity-10 rounded-full blur-[100px] pointer-events-none"></div>

            <div className="max-w-4xl mx-auto px-6 text-center text-white relative z-10">
                <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight">Pronto para transformar seu escritório?</h2>
                <p className="text-xl text-blue-100 mb-10 font-light max-w-2xl mx-auto">
                    Fale diretamente pelo WhatsApp com nossos consultores especializados. Vamos entender sua demanda e mostrar o poder do ADVtools na prática.
                </p>
                <a
                    href={waLink}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center justify-center gap-3 bg-[#25D366] text-white px-8 py-5 rounded-full font-bold text-lg hover:bg-[#1ebd5a] transition-all shadow-[0_10px_30px_rgba(37,211,102,0.3)] hover:shadow-[0_10px_40px_rgba(37,211,102,0.4)] hover:scale-105"
                >
                    <MessageCircle className="w-6 h-6" />
                    Falar via WhatsApp
                </a>
            </div>

            <div className="mt-24 text-center text-blue-300/60 text-sm w-full relative z-10">
                © {new Date().getFullYear()} ADVtools. Todos os direitos reservados.
            </div>
        </section>
    );
}
