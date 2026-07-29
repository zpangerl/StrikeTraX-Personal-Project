<template>
  <div class="text-center mt-3 pt-4">
    <h1 class="display-1" style="color: red;"><strong>Bowling Score Tracker</strong></h1>
    <p style="color: red">Landing Page</p>
  </div>
  <div class="d-flex justify-content-center">
    <div>
      <p>Frame: {{ currentFrame }}</p>
      <p>Roll: {{ currentRoll }}</p>
      <select v-model.number="rollDropdown" v-if="!isEndOfGame">
        <option v-for="n in pins" :key="n - 1" :value="n - 1">{{ n - 1 }}</option>
        <option :value="remainingPins">{{ strikeOrSpare }}</option>
      </select>
      <button @click="handleSubmit" :disabled="rollDropdown === ''" v-if="!isEndOfGame">Submit</button>
    </div>
  </div>
  <div class="d-flex justify-content-center">
    <div class="scorecard d-flex">
      <div v-for="(frame, i) in frames" :key="i" class="frame-wrapper text-center me-2">
        <div class="frame-number mb-1">{{ i + 1 }}</div>
        <div class="frame-cell">
          <div class="roll-boxes">
            <div class="roll-box">{{ displayRoll(frame, 1) }}</div>
            <div class="roll-box">{{ displayRoll(frame, 2) }}</div>
            <div class="roll-box" v-if="frame.roll3 !== undefined">{{ displayRoll(frame, 3) }}</div>
          </div>
        <div class="frame-total">{{ frame.currentTotal }}</div>
        </div>
      </div>
    </div>
  </div>
  <div class="d-flex justify-content-center">
    <p v-if="isEndOfGame">Total Score: {{ total }}</p>
  </div>
  <div class="d-flex justify-content-center">
    <button @click="newGame" v-if="isEndOfGame">Reset Without Saving</button>
    <!--Need to add a new function for the button below that logs the game in localStorage for now, DB later, and then resets-->
    <button @click="newGame" v-if="isEndOfGame">Log Game</button>
  </div>
</template>

<script>
  import { ref, computed, watch } from 'vue'
  export default {
    setup(){

      var isEndOfGame = ref(false)
      var total = ref(0)
      var currentFrame = ref(1)
      var currentRoll = ref(1)
      var firstRoll = null
      var secondRoll = null
      var throws = []
      var frames = ref([])
      frames.value = initializeFrames()

      const rollDropdown = ref('')

      var pins = ref([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
      var remainingPins = ref(10)

      const loadThrows = localStorage.getItem('throws')

      if (loadThrows !== null){
        loadGame()
      }
      else if (currentFrame.value < 1 || currentFrame.value > 10) newGame()

      const strikeOrSpare = computed (() => {
        if (currentFrame.value !== 10 && currentRoll.value === 1) return 'X'
        else if (currentFrame.value !== 10 && currentRoll.value === 2) return '/'
        else if (currentFrame.value === 10 && currentRoll.value === 1) return 'X'
        else if (currentFrame.value === 10 && currentRoll.value === 2 && firstRoll === 10) return 'X'
        else if (currentFrame.value === 10 && currentRoll.value === 2 && firstRoll !== 10) return '/'
        else if (currentFrame.value === 10 && currentRoll.value === 3 && remainingPins.value === 10) return 'X'
        else if (currentFrame.value === 10 && currentRoll.value === 3 && remainingPins.value !== 10) return '/'
        else return 'error'
      })

      function computeSecondRoll(){
        const pinsLeft = remainingPins.value - firstRoll
        pins.value.length = 0
        for (let i = 1; i <= pinsLeft; i++){
          pins.value.push(i)
        }
        return pinsLeft
      }

      function computeThirdRoll(){
        const pinsLeft = remainingPins.value - secondRoll
        pins.value.length = 0
        for (let i = 1; i <= pinsLeft; i++){
          pins.value.push(i)
        }
        return pinsLeft
      }

      function resetPins(){
        pins.value.length = 0
        for (let i = 1; i <= 10; i++){
          pins.value.push(i)
        }
      }

      function handleSubmit(){
        if (currentFrame.value > 0 && currentFrame.value < 10){
          if (currentRoll.value === 1){
            firstRoll = rollDropdown.value
            addThrow(firstRoll)
            if (firstRoll === 10){
              firstRoll = null
              remainingPins.value = 10
              currentFrame.value++
              return
            }
            remainingPins.value = computeSecondRoll()
            currentRoll.value++
            return
          }
          else{
            addThrow(rollDropdown.value)
            firstRoll = null
            currentRoll.value = 1
            currentFrame.value++
            remainingPins.value = 10
            resetPins()
            return
          }
        }
        else if (currentFrame.value === 10){
          if (currentRoll.value === 1){
            firstRoll = rollDropdown.value
            addThrow(firstRoll)
            if (firstRoll === 10){
              remainingPins.value = 10
              currentRoll.value++
              return
            }
            remainingPins.value = computeSecondRoll()
            currentRoll.value++
            return
          }
          else if (currentRoll.value === 2){
            secondRoll = rollDropdown.value
            addThrow(secondRoll)
            if (firstRoll === 10){
              if (secondRoll === 10){
                remainingPins.value = 10
                currentRoll.value++
                return
              }
              remainingPins.value = computeThirdRoll()
              currentRoll.value++
              return
            }
            if (secondRoll === remainingPins.value){
              currentRoll.value++
              remainingPins.value = 10
              resetPins()
              return
            }
            else {
              isEndOfGame.value = true
              return
            }
          }
          else if (currentRoll.value === 3){
            addThrow(rollDropdown.value)
            isEndOfGame.value = true
            return
          }
        }
      }

      function displayRoll(frame, rollNum){
        const roll = frame[`roll${rollNum}`]
        if (roll === null) return ''

        if (roll === 10) return 'X'
        else if (frame.frame === 10 && roll === 10) return 'X'
        else if (rollNum === 2 && frame.roll1 + roll === 10 && frame.roll1 !== 10) return '/'
        else if (rollNum === 3 && frame.roll2 + roll === 10 && frame.roll2 !== 10) return '/'
        else return roll
      }

      function addThrow(newThrow){
        throws.push(newThrow)
        rollDropdown.value = ''
        savePartialGame(throws)
        const scoreJSON = calculateScore(throws)
        if (!scoreJSON.isValid || scoreJSON.frames === null || scoreJSON.total === null){
          // for now, will update later to actually resolve back to previous throw/frame/whatever if invalid
          newGame()
          return
        }
        else {
          frames.value = scoreJSON.frames
          total.value = scoreJSON.total
        }
      }

      function calculateScore(throwsArray){
        var throwsIter = 0
        var currentThrow = 1
        var currentFrame = 1
        var totalPinsThisFrame = 0
        var currentTotal = 0
        let gameFrames = initializeFrames()
        const returnJSON = {
          frames: null,
          isValid: true,
          currThrow: 1,
          currFrame: 1,
          pinsLeft: 10,
          total: null
        }

        while (throwsIter < throwsArray.length){
          var nextThrow = throwsArray[throwsIter]
          if (typeof nextThrow !== 'number' || nextThrow < 0 || nextThrow > (10 - totalPinsThisFrame)){
            returnJSON.isValid = false
            return returnJSON
          }
          if (currentThrow === 1 && nextThrow === 10 && currentFrame !== 10){
            if (throwsIter + 2 >= throwsArray.length) {
              if (throwsArray[throwsIter + 1] !== undefined){
                gameFrames[currentFrame].roll1 = throwsArray[throwsIter + 1]
              }
              gameFrames[currentFrame - 1].roll1 = nextThrow
              returnJSON.frames = gameFrames
              returnJSON.currThrow = currentThrow
              returnJSON.currFrame = currentFrame
              returnJSON.pinsLeft = 10 - totalPinsThisFrame
              returnJSON.total = currentTotal
              return returnJSON
            }
            totalPinsThisFrame += nextThrow
            currentTotal += nextThrow
            currentTotal += throwsArray[throwsIter + 1]
            currentTotal += throwsArray[throwsIter + 2]
            gameFrames[currentFrame - 1].roll1 = nextThrow
            gameFrames[currentFrame - 1].currentTotal = currentTotal
            currentThrow++
          }
          else if (currentThrow === 2 && nextThrow === (10 - totalPinsThisFrame) && currentFrame !== 10){
            if (throwsIter + 1 >= throwsArray.length) {
              gameFrames[currentFrame - 1].roll2 = nextThrow
              gameFrames[currentFrame - 1].currentTotal = null
              returnJSON.frames = gameFrames
              returnJSON.currThrow = currentThrow
              returnJSON.currFrame = currentFrame
              returnJSON.pinsLeft = 10 - totalPinsThisFrame
              returnJSON.total = currentTotal
              return returnJSON
            }
            totalPinsThisFrame += nextThrow
            currentTotal += nextThrow
            currentTotal += throwsArray[throwsIter + 1]
            gameFrames[currentFrame - 1].roll2 = nextThrow
            gameFrames[currentFrame - 1].currentTotal = currentTotal
            currentThrow++
          }
          else if (currentFrame === 10){
            if (currentThrow === 1){
              if (nextThrow !== 10){
                totalPinsThisFrame += nextThrow
              }
              else totalPinsThisFrame = 0
            }
            else if (currentThrow === 2){
              if (gameFrames[currentFrame - 1].roll1 === 10){
                if (nextThrow === 10){
                  totalPinsThisFrame = 0
                }
                else {
                  totalPinsThisFrame += nextThrow
                }
              }
              else{
                if (nextThrow === (10 - totalPinsThisFrame)){
                  totalPinsThisFrame = 0
                }
                else{
                  totalPinsThisFrame = 10
                  currentTotal += nextThrow
                  gameFrames[currentFrame - 1].roll2 = nextThrow
                  gameFrames[currentFrame - 1].currentTotal = currentTotal
                  currentThrow++
                  break
                }
              }
            }
            else if (currentThrow === 3){
              currentTotal += nextThrow
              gameFrames[currentFrame - 1].roll3 = nextThrow
              gameFrames[currentFrame - 1].currentTotal = currentTotal
              currentThrow++
              break
            }
            currentTotal += nextThrow
            gameFrames[currentFrame - 1][`roll${currentThrow}`] = nextThrow
            gameFrames[currentFrame - 1].currentTotal = currentTotal
            currentThrow++
          }
          else{
            totalPinsThisFrame += nextThrow
            currentTotal += nextThrow
            gameFrames[currentFrame - 1][`roll${currentThrow}`] = nextThrow
            if (currentThrow != 1){
              gameFrames[currentFrame - 1].currentTotal = currentTotal
            }
            currentThrow++
          }
          if (((currentThrow > 2 || totalPinsThisFrame === 10) && currentFrame !== 10)){
            currentThrow = 1
            gameFrames[currentFrame - 1].currentTotal = currentTotal
            currentFrame++
            totalPinsThisFrame = 0
          }
          throwsIter++
        }
        returnJSON.total = currentTotal
        returnJSON.currThrow = currentThrow
        returnJSON.currFrame = currentFrame
        returnJSON.pinsLeft = 10 - totalPinsThisFrame
        returnJSON.frames = gameFrames
        return returnJSON
      }

      function savePartialGame(throwsArray){
        localStorage.setItem('throws', JSON.stringify(throwsArray))
      }

      function newGame(){
        currentFrame.value = 1
        currentRoll.value = 1
        remainingPins.value = 10
        firstRoll = null
        secondRoll = null
        throws.length = 0
        frames.value.length = 0
        // make sure game is saved before doing what's below
        localStorage.removeItem('throws')
        frames.value = initializeFrames()
        total.value = 0
        resetPins()
        isEndOfGame.value = false
      }

      function initializeFrames(){
        let framesArr = []
        for (var i = 0; i < 9; i++){
          framesArr.push({ frame: i + 1, roll1: null, roll2: null, currentTotal: null })
        }
        framesArr.push({ frame: 10, roll1: null, roll2: null, roll3: null, currentTotal: null })
        return framesArr
      }

      function loadGame(){
        if (localStorage.getItem('throws') !== null){
          // load, parse, and validate throws array
          try{
          throws = JSON.parse(localStorage.getItem('throws'))
          } catch (error){
            newGame()
            alert("Invalid save data, starting new game")
            return
          }
          currentFrame.value = 1
          currentRoll.value = 1
          var throwsIter = 0
          var firstRollLoad = null
          var secondRollLoad = null
          var thirdRollLoad = null
          var remainingPinsLoad = 10
          while (throwsIter < throws.length){
            if (currentFrame.value > 0 && currentFrame.value < 10){
              if (currentRoll.value === 1){
                firstRollLoad = throws[throwsIter]
                if (!validateThrow(firstRollLoad, remainingPinsLoad)){
                  newGame()
                  return
                }
                throwsIter++
                //frames.value[currentFrame.value - 1]['roll1'] = firstRollLoad
                if (firstRollLoad === 10){
                  //handle strike
                  currentFrame.value++
                  continue
                }
                else {
                  remainingPinsLoad = 10 - firstRollLoad
                  currentRoll.value++
                }
              }
              else {
                secondRollLoad = throws[throwsIter]
                if (!validateThrow(secondRollLoad, remainingPinsLoad)){
                  newGame()
                  return
                }
                throwsIter++
                //frames.value[currentFrame.value - 1]['roll2'] = secondRollLoad
                firstRollLoad = null
                currentRoll.value = 1
                currentFrame.value++
                remainingPinsLoad = 10
              }
            }
            else if (currentFrame.value === 10){
              if (currentRoll.value === 1){
                firstRollLoad = throws[throwsIter]
                if (!validateThrow(firstRollLoad, remainingPinsLoad)){
                  newGame()
                  return
                }
                throwsIter++
                //frames.value[currentFrame.value - 1].roll1 = firstRollLoad
                currentRoll.value++
                if (firstRollLoad !== 10){
                  remainingPinsLoad = 10 - firstRollLoad
                }
                else {
                  remainingPinsLoad = 10
                }
                continue
              }
              else if (currentRoll.value === 2){
                secondRollLoad = throws[throwsIter]
                if (!validateThrow(secondRollLoad, remainingPinsLoad)){
                  newGame()
                  return
                }
                throwsIter++
                //frames.value[currentFrame.value - 1].roll2 = secondRollLoad
                if (firstRollLoad === 10){
                  if (secondRollLoad === 10){
                    currentRoll.value++
                    continue
                  }
                  remainingPinsLoad = remainingPinsLoad - secondRollLoad
                  currentRoll.value++
                  continue
                }
                if (secondRollLoad === remainingPinsLoad){
                  currentRoll.value++
                  remainingPinsLoad = 10
                  continue
                }
                else{
                  if (throwsIter !== throws.length){
                    newGame()
                    return
                  }
                  isEndOfGame.value = true
                  break
                }
              }
              else if (currentRoll.value === 3){
                thirdRollLoad = throws[throwsIter]
                throwsIter++
                if (!validateThrow(thirdRollLoad, remainingPinsLoad)){
                  newGame()
                  return
                }
                //frames.value[currentFrame.value - 1].roll3 = thirdRollLoad
                if (throwsIter !== throws.length){
                  newGame()
                  return
                }
                isEndOfGame.value = true
                break
              }
            }
          }
          remainingPins.value = remainingPinsLoad
          pins.value.length = 0
          for (let i = 1; i <= remainingPins.value; i++){
            pins.value.push(i)
          }
          firstRoll = firstRollLoad
          secondRoll = secondRollLoad
          const scoreJSON = calculateScore(throws)
          if (!scoreJSON.isValid || scoreJSON.frames === null){
          // for now, will update later to actually resolve back to previous throw/frame/whatever if invalid
            newGame()
            return
          }
          else {
            frames.value = scoreJSON.frames
            total.value = scoreJSON.total
          }
        }
      }

      function validateThrow(throwVal, pinsVal){
        if (throwVal >= 0 && throwVal <= pinsVal){
          return true
        }
        else return false
      }

      return {
        isEndOfGame,
        currentFrame,
        currentRoll,
        firstRoll,
        secondRoll,
        throws,
        frames,
        pins,
        rollDropdown,
        strikeOrSpare,
        remainingPins,
        total,
        addThrow,
        displayRoll,
        computeSecondRoll,
        computeThirdRoll,
        handleSubmit,
        newGame,
        initializeFrames,
        savePartialGame,
        loadGame,
        validateThrow,
      }
    }
  }
</script>

<style>
    body { background-color:  darkslategrey; }
</style>

<style scoped>

  .scorecard {
    overflow-x: auto;
    padding-bottom: 0.5rem;
  }

  .frame-cell {
    position: relative;
    width: 70px;
    height: 70px;
    border: 1px solid #333;
  }

  .roll-boxes {
    position: absolute;
    top: 0;
    right: 0;
    display: flex;
  }

  .roll-box {
    width: 20px;
    height: 20px;
    border-left: 1px solid #333;
    border-bottom: 1px solid #333;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
  }

  .frame-total {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
  }
</style>