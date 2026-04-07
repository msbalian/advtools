export const getWhatsAppLink = (phone: string, text: string) => {
    const encodedText = encodeURIComponent(text);
    const cleanPhone = phone.replace(/\D/g, ''); // Removes non-numeric char
    return `https://wa.me/55${cleanPhone}?text=${encodedText}`;
};
