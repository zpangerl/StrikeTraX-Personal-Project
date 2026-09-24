import { ref } from 'vue'

export function requestWithRetry(){
    const isWakingUp = ref(false)

    async function fetchWithRetry(url, options) {
        const startTime = Date.now()
        // Timer to show load page after two seconds if first request hasn't been answered.
        const timer = setTimeout(() => {
            isWakingUp.value = true
        }, 2000)
        // set up end time
        const endTime = startTime + 120000 //120 seconds

        let response = null
        try{
            while (Date.now() < endTime){
                response = await fetch(url, options)
                if (response.status === 503 && Date.now() < endTime){
                    isWakingUp.value = true
                    // wait for 10 seconds
                    await new Promise(resolve => setTimeout(resolve, 10000))
                }
                else if (response.status === 503 && Date.now() >= endTime){
                    return response
                }
                else if (response.status !== 503){
                    return response
                }
            }
        }
        finally {
            clearTimeout(timer)
            isWakingUp.value = false
        }
        return response
    }

    return { isWakingUp, fetchWithRetry }
}