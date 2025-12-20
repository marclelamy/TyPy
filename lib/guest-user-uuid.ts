import { v4 as uuidv4 } from 'uuid'

type StorageResult = {
    success: boolean
    value: string
    error?: unknown
}

// All getOrCreate functions now take a `uuid` argument and will use it as the identifier if needed.
function getOrCreateLocalStorageIdentifier(uuid: string): StorageResult {
    try {
        const key = 'random_id'
        let identifier = localStorage.getItem(key)
        
        if (!identifier) {
            identifier = uuid
            localStorage.setItem(key, identifier)
        }
        
        return { success: true, value: identifier }
    } catch (e) {
        return { success: false, value: '', error: e }
    }
}

function getOrCreateCookieIdentifier(uuid: string): StorageResult {
    try {
        const key = 'blend_ai_cookie_id'
        const match = document.cookie.match(new RegExp('(^| )' + key + '=([^;]+)'))
        let identifier = match ? match[2] : null
        
        if (!identifier) {
            identifier = uuid
            document.cookie = `${key}=${identifier}; path=/`
            
            // Verify cookie was actually set
            const verifyMatch = document.cookie.match(new RegExp('(^| )' + key + '=([^;]+)'))
            if (!verifyMatch) {
                return { success: false, value: '', error: 'Failed to set cookie' }
            }
        }
        
        return { success: true, value: identifier }
    } catch (e) {
        return { success: false, value: '', error: e }
    }
}

function getOrCreateSessionStorageIdentifier(uuid: string): StorageResult {
    try {
        const key = 'blend_ai_session_id'
        let identifier = sessionStorage.getItem(key)
        
        if (!identifier) {
            identifier = uuid
            sessionStorage.setItem(key, identifier)
        }
        
        return { success: true, value: identifier }
    } catch (e) {
        return { success: false, value: '', error: e }
    }
}

async function getOrCreateIndexedDBIdentifier(uuid: string): Promise<StorageResult> {
    return new Promise((resolve) => {
        try {
            const key = 'blend_ai_indexeddb_id'
            const dbName = 'BlendAIUserDB'
            const storeName = 'userIdentifiers'
            
            const request = indexedDB.open(dbName, 1)
            
            request.onupgradeneeded = (event) => {
                const db = request.result
                if (!db.objectStoreNames.contains(storeName)) {
                    db.createObjectStore(storeName, { keyPath: 'id' })
                }
            }
            
            request.onerror = () => {
                resolve({ success: false, value: '', error: 'IndexedDB access denied' })
            }
            
            request.onsuccess = () => {
                const db = request.result
                const tx = db.transaction(storeName, 'readwrite')
                const store = tx.objectStore(storeName)
                
                const getRequest = store.get(key)
                
                getRequest.onsuccess = () => {
                    if (getRequest.result) {
                        resolve({ success: true, value: getRequest.result.value })
                    } else {
                        const identifier = uuid
                        store.put({ id: key, value: identifier })
                        resolve({ success: true, value: identifier })
                    }
                }
                
                getRequest.onerror = () => {
                    resolve({ success: false, value: '', error: 'Failed to retrieve IndexedDB identifier' })
                }
                
                tx.oncomplete = () => {
                    db.close()
                }
            }
        } catch (e) {
            resolve({ success: false, value: '', error: e })
        }
    })
}


export async function checkOrCreateUserIdentifiers(): Promise<Record<string, string>> {
    const uuid = uuidv4()

    const identifiers: Record<string, string> = {}
    
    // Use same uuid for every mechanism
    const localStorage = getOrCreateLocalStorageIdentifier(uuid)
    const cookies = getOrCreateCookieIdentifier(uuid)
    const sessionStorage = getOrCreateSessionStorageIdentifier(uuid)
    const indexedDB = await getOrCreateIndexedDBIdentifier(uuid)
    
    if (localStorage.success) identifiers.localStorage = localStorage.value
    if (cookies.success) identifiers.cookie = cookies.value
    if (sessionStorage.success) identifiers.sessionStorage = sessionStorage.value
    if (indexedDB.success) identifiers.indexedDB = indexedDB.value
    
    if (!localStorage.success && !cookies.success && !sessionStorage.success && !indexedDB.success) {
        throw new Error("No storage mechanism available - this is required to use the app")
    }
    
    return identifiers
}