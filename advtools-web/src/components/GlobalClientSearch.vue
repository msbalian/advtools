<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from 'lucide-vue-next'
import { apiFetch } from '../utils/api'

const router = useRouter()
const props = defineProps({
  placeholder: {
    type: String,
    default: "Buscar clientes por nome, CPF ou CNPJ..."
  },
  autoFocus: {
    type: Boolean,
    default: false
  }
})

const searchQuery = ref('')
const isFocused = ref(false)
const clientes = ref([])
const filteredClientes = ref([])
const isLoading = ref(false)
const searchContainer = ref(null)

// Load all clients once (assuming the list is manageable for frontend filtering)
const loadClientes = async () => {
  isLoading.value = true
  try {
    const response = await apiFetch('/api/clientes')
    if (response.ok) {
      clientes.value = await response.json()
    }
  } catch (error) {
    console.error("Erro ao carregar clientes para busca:", error)
  } finally {
    isLoading.value = false
  }
}

// Filter clients based on search query
watch(searchQuery, (newQuery) => {
  if (!newQuery) {
    filteredClientes.value = []
    return
  }
  
  const term = newQuery.toLowerCase()
  filteredClientes.value = clientes.value.filter(cliente => {
    return (cliente.nome && cliente.nome.toLowerCase().includes(term)) ||
           (cliente.documento && cliente.documento.includes(term)) ||
           (cliente.email && cliente.email.toLowerCase().includes(term))
  }).slice(0, 10) // Limit to 10 results
})

const selectCliente = (cliente) => {
  searchQuery.value = ''
  isFocused.value = false
  router.push(`/clientes/${cliente.id}`)
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (searchContainer.value && !searchContainer.value.contains(event.target)) {
    isFocused.value = false
  }
}

const inputRef = ref(null)

onMounted(() => {
  loadClientes()
  document.addEventListener('mousedown', handleClickOutside)
  if (props.autoFocus) {
    setTimeout(() => {
        inputRef.value?.focus()
    }, 100)
  }
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})

</script>

<template>
  <div class="relative w-full" ref="searchContainer">
    <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
      <Search class="h-5 w-5 text-slate-400" aria-hidden="true" />
    </div>
    <input 
      v-model="searchQuery"
      @focus="isFocused = true"
      ref="inputRef"
      type="text" 
      class="block w-full rounded-full border-0 py-1.5 pl-10 pr-3 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 bg-slate-50 transition-colors" 
      :placeholder="placeholder" 
    />
    
    <!-- Dropdown -->
    <div 
      v-if="isFocused && (searchQuery.length > 0 || isLoading)" 
      class="absolute z-50 mt-1 w-full bg-white shadow-lg rounded-xl border border-slate-200 overflow-hidden"
    >
      <div v-if="isLoading" class="p-4 text-center text-sm text-slate-500">
        Carregando clientes...
      </div>
      
      <div v-else-if="searchQuery && filteredClientes.length === 0" class="p-4 text-center text-sm text-slate-500">
        Nenhum cliente encontrado para "{{ searchQuery }}"
      </div>

      <ul v-else class="max-h-80 overflow-y-auto py-1">
        <li 
          v-for="cliente in filteredClientes" 
          :key="cliente.id"
          @click="selectCliente(cliente)"
          class="px-4 py-2 hover:bg-slate-50 cursor-pointer flex flex-col transition-colors border-b border-slate-50 last:border-0"
        >
          <span class="text-sm font-medium text-slate-900">{{ cliente.nome }}</span>
          <span class="text-xs text-slate-500 flex items-center gap-2">
             <span v-if="cliente.documento">{{ cliente.documento }}</span>
             <span v-if="cliente.email"> • {{ cliente.email }}</span>
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>
