/**
 * Used to retry requests to the database, while the database is waking up from being paused.
 * 
 * Used by both Scoring.vue and History.vue.
 */
import { ref } from 'vue'

/**
 * Used to supply the a ref and a function to both History.vue and Scoring.vue.
 * @returns {{ isWakingUp: Ref<boolean>, fetchWithRetry: Function}} - An object with a reactive ref
 * that is true when a request is being retried, and a function similar to fetch that automatically retries
 * when the response is a 503.
 */
export function requestWithRetry(){
    const isWakingUp = ref(false)
    const retryTimeTotal = 120000 // 120 seconds
    const retryTimeSingle = 10000 // 10 seconds

    /**
     * Attempts to query the database, retrying for a set period of time if it is unsuccessful.
     * @param {string} url - The complete url to the database, including endpoint.
     * @param {RequestInit} [options] - The request body being sent.
     * @returns 
     */
    async function fetchWithRetry(url, options) {
        const startTime = Date.now()
        // Timer to show load page after two seconds if first request hasn't been answered.
        const timer = setTimeout(() => {
            isWakingUp.value = true
        }, 2000)
        // set up end time
        const endTime = startTime + retryTimeTotal

        let response = null
        try{
            while (Date.now() < endTime){
                response = await fetch(url, options)
                if (response.status === 503 && Date.now() < endTime){
                    isWakingUp.value = true
                    // wait for 10 seconds
                    await new Promise(resolve => setTimeout(resolve, retryTimeSingle))
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