<template>
    <div class="text-center mt-3 pt-4">
        <h1 class="display-1" style="color: black"><strong>StrikeTraX</strong></h1>
        <p style="color: black">Home Page</p>
    </div>
    <div class="d-flex justify-content-center">
        <button @click="enterGame">Enter Game</button>
        <button @click="enterHistory">History</button>
    </div>
</template>

<script>
    import {useRouter} from 'vue-router'

    export default {
        setup(){
            const router = useRouter()
            function enterGame(){
                router.push('/scoring')
            }
            function enterHistory(){
                router.push('/history')
            }
            return { enterGame, enterHistory }
        }
    }
</script>