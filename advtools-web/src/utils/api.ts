import router from '../router'

/**
 * A wrapper around native fetch that automatically includes the auth token
 * and handles 401 Unauthorized errors by logging the user out.
 */
export async function apiFetch(input: RequestInfo | URL, init: RequestInit = {}) {
    const token = localStorage.getItem('advtools_token')

    // Set up headers
    const headers = new Headers(init.headers || {})
    if (token) {
        // Only set Authorization if not already set by the caller
        if (!headers.has('Authorization')) {
            headers.set('Authorization', `Bearer ${token}`)
        }
    }

    // Only set Content-Type to JSON if it's not FormData and not already set.
    // The browser automatically sets Content-Type: multipart/form-data with the correct boundary for FormData.
    if (init.body && !(init.body instanceof FormData) && !headers.has('Content-Type')) {
        // If the body is a plain object, assume it should be JSON
        if (typeof init.body === 'object') {
            headers.set('Content-Type', 'application/json')
        }
        // If the body is a string, and no Content-Type is set, assume JSON
        else if (typeof init.body === 'string') {
            headers.set('Content-Type', 'application/json')
        }
    }

    const response = await fetch(input, {
        ...init,
        headers
    })

    // Global 401 Unauthorized handling
    if (response.status === 401) {
        console.warn("Sessão expirada ou inválida. Redirecionando para login...")
        localStorage.removeItem('advtools_token')
        // Use the router to redirect
        if (router.currentRoute.value.path !== '/') {
            router.push('/')
        }
        // Optionally throw an error to stop the execution of the calling function
        throw new Error('Sessão expirada. Por favor, faça login novamente.')
    }

    return response
}

/**
 * Baixa um arquivo protegido do backend usando apiFetch (passando token)
 */
export async function downloadFile(relPath: string, filename?: string) {
    // Se o path já vier com /static/ ou similar, limpamos para a rota de download
    let cleanPath = relPath.replace(/^static\//, '').replace(/^armazenamento\//, 'armazenamento/')
    
    // Se não começar com armazenamento/, mas for um doc do cliente, adicionamos
    if (!cleanPath.startsWith('armazenamento/') && !cleanPath.startsWith('logos/')) {
        cleanPath = `armazenamento/${cleanPath}`
    }

    const res = await apiFetch(`/api/arquivos/download/${cleanPath}`)
    if (!res.ok) {
        throw new Error('Não foi possível baixar o arquivo. Verifique se ele ainda existe.')
    }

    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || cleanPath.split('/').pop() || 'arquivo'
    document.body.appendChild(a)
    a.click()
    // Pequeno delay para garantir que o browser iniciou o download antes de remover o objeto
    setTimeout(() => {
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
    }, 100)
}
