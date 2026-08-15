<template>
  <div class="text-center mt-3 pt-4">
    <h1 class="display-5"><strong>Log Game</strong></h1>
  </div>
  <div class="d-flex justify-content-center">
    <div>
      <p>Frame: {{ currentFrame }}</p>
      <p>Roll: {{ currentRoll }}</p>
      <select class="form-select" v-model.number="rollDropdown" v-if="!isEndOfGame">
        <!--This will display 0 to max current pins - 1-->
        <option v-for="n in pins" :key="n - 1" :value="n - 1">{{ n - 1 }}</option>
        <!--Determine whether to display / or X in the final dropdown selection-->
        <option :value="remainingPins">{{ strikeOrSpare }}</option>
      </select>
      <button class="btn btn-primary" @click="handleSubmit" :disabled="rollDropdown === ''" v-if="!isEndOfGame">Submit</button>
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
    <p class="display-6" v-if="isEndOfGame">Total Score: {{ total }}</p>
  </div>
  <div class="d-flex justify-content-center">
    <button class="btn btn-danger" @click="newGame" v-if="isEndOfGame">Reset Without Saving</button>
    <button class="btn btn-primary" @click="saveGame" v-if="isEndOfGame">Log Game</button>
  </div>
</template>

<script setup>
  import { ref, computed } from 'vue'
  import { displayRoll, calculateScore, initializeFrames, validateThrow } from '../utils/scoring'
  import { loadPartialGame, clearPartialGame, loadCompleteGames, saveCompleteGames, savePartialGame } from '../utils/gameStorage'

  const isEndOfGame = ref(false)
  const total = ref(0)
  const currentFrame = ref(1)
  const currentRoll = ref(1)
  let firstRoll = null
  let secondRoll = null
  let throws = []
  const frames = ref([])
  frames.value = initializeFrames()

  const rollDropdown = ref('')

  // need an actual array here since dropdown values are directly derived from it
  const pins = ref([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
  const remainingPins = ref(10)

  const loadThrows = localStorage.getItem('throws')

  if (loadThrows !== null){
    loadGame()
  }
  // if for some reason currentFrame is out of bounds, reset the game
  // realistically only possible with devtools
  else if (currentFrame.value < 1 || currentFrame.value > 10) newGame()

  /**
   * Determines if a 'X' or '/' should be displayed in the final option of the score dropdown.
   * @returns {string} - 'X' if the max throw is a strike, '/' if the max throw is a spare, and 'error' if state data is invalid.
   */
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

  /**
   * Determines how many pins are remaining for second/third rolls if the previous roll was not a strike.
   * @param {number} previousRoll - The previous roll in the frame.
   * @returns {number} - The number of pins remaining.
   */
  function computeRemainingPins(previousRoll){
    const pinsLeft = remainingPins.value - previousRoll
    pins.value.length = 0
    for (let i = 1; i <= pinsLeft; i++){
      pins.value.push(i)
    }
    return pinsLeft
  }

  /**
   * Resets the pins array to a full stack of pins (1-10).
   */
  function resetPins(){
    pins.value.length = 0
    for (let i = 1; i <= 10; i++){
      pins.value.push(i)
    }
  }

  /**
   * Handles the current roll's submission:
   * 
   * 1. Determines strike/spare/open frame
   * 2. Updates state variables accordingly
   * 3. Calls addThrow to add the throw to the throws array
   */
  function handleSubmit(){
    let throwAdded = true
    // all frames but frame 10, which is a special case
    if (currentFrame.value > 0 && currentFrame.value < 10){
      // first throw, need to account for possible strike
      if (currentRoll.value === 1){
        firstRoll = rollDropdown.value
        throwAdded = addThrow(firstRoll)
        if (!throwAdded) return
        // handle strike
        if (firstRoll === 10){
          firstRoll = null
          remainingPins.value = 10
          currentFrame.value++
          return
        }
        remainingPins.value = computeRemainingPins(firstRoll)
        currentRoll.value++
        return
      }
      // second throw, need to update state to next frame and reset pins
      else{
        throwAdded = addThrow(rollDropdown.value)
        if (!throwAdded) return
        firstRoll = null
        currentRoll.value = 1
        currentFrame.value++
        remainingPins.value = 10
        resetPins()
        return
      }
    }
    // tenth frame specifically, special case since it can have three frames
    else if (currentFrame.value === 10){
      // first throw, need to check for a strike
      if (currentRoll.value === 1){
        firstRoll = rollDropdown.value
        throwAdded = addThrow(firstRoll)
        if (!throwAdded) return
        if (firstRoll === 10){
          remainingPins.value = 10
          currentRoll.value++
          return
        }
        remainingPins.value = computeRemainingPins(firstRoll)
        currentRoll.value++
        return
      }
      // second roll, need to check for both a strike and a spare, since tenth frame throw 2 can have either, or none
      else if (currentRoll.value === 2){
        secondRoll = rollDropdown.value
        throwAdded = addThrow(secondRoll)
        if (!throwAdded) return
        // first throw strike
        if (firstRoll === 10){
          // second roll strike
          if (secondRoll === 10){
            remainingPins.value = 10
            currentRoll.value++
            return
          }
          // second roll not a strike, continue to throw 3
          remainingPins.value = computeRemainingPins(secondRoll)
          currentRoll.value++
          return
        }
        // second roll a spare, continue to throw 3
        if (secondRoll === remainingPins.value){
          currentRoll.value++
          remainingPins.value = 10
          resetPins()
          return
        }
        // second roll isn't a strike, spare, or isn't immediately after a first roll strike, so the game ends
        else {
          isEndOfGame.value = true
          return
        }
      }
      // third roll
      else if (currentRoll.value === 3){
        throwAdded = addThrow(rollDropdown.value)
        if (!throwAdded) return
        isEndOfGame.value = true
        return
      }
    }
  }

  /**
   * Adds the current throw to the throws array and calls calculateScore to update scores, frames, and rolling total.
   * Also calls for saving of the partial throws array for persistence.
   * On invalid data, resets the game.
   * @param {number} newThrow - The current throw to be added.
   * @returns {boolean} - True if the throw was added successfully, false if adding it resulted in invalid game state, which then resets the game.
   */
  function addThrow(newThrow){
    throws.push(newThrow)
    rollDropdown.value = ''
    savePartialGame(throws)
    const scoreJSON = calculateScore(throws)
    if (!scoreJSON.isValid || scoreJSON.frames === null || scoreJSON.total === null){
      // Reset the game, this branch requires the dropdown menu specifically containing invalid data, which shouldn't be possible outside of devtools
      newGame()
      return false
    }
    else {
      frames.value = scoreJSON.frames
      total.value = scoreJSON.total
      return true
    }
  }

  /**
   * Resets state variables and clears partial game storage to facilitate starting a new game
   */
  function newGame(){
    currentFrame.value = 1
    currentRoll.value = 1
    remainingPins.value = 10
    firstRoll = null
    secondRoll = null
    throws.length = 0
    frames.value.length = 0
    clearPartialGame()
    frames.value = initializeFrames()
    total.value = 0
    resetPins()
    isEndOfGame.value = false
  }

  /**
   * Saves a completed game to the Azure SQL database
   */  
  async function saveGame(){
    let sessionID = localStorage.getItem('sessionID')
    if (sessionID === null){
      sessionID = crypto.randomUUID()
      localStorage.setItem('sessionID', sessionID)
    }
    // actually save the game from here on
    const response = await fetch('http://127.0.0.1:8000/games', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        throws: throws,
        total_score: total.value,
        session_id: sessionID
      })
    })
    if(response.status === 422){
      alert("Game contained invalid data, starting new game")
      newGame()
    }
    else if(!response.ok){
      alert("Your game could not be saved, please try again")
      return
    }
    else{
      alert("Game was saved!")
      newGame()
    }
  }

/**
   * Loads a partial game from localStorage and prepares it to be displayed and continued.
   * 
   * Walks through the throws array, validates all throws, and updates state variables.
   */
  function loadGame(){
    if (localStorage.getItem('throws') !== null){
      // if the saved partial game is invalid data, just purge and start a new game
      try{
      throws = loadPartialGame()
      } catch (error){
        newGame()
        alert("Invalid save data, starting new game")
        return
      }
      currentFrame.value = 1
      currentRoll.value = 1
      let throwsIter = 0
      let firstRollLoad = null
      let secondRollLoad = null
      let thirdRollLoad = null
      let remainingPinsLoad = 10
      // walk through throws array
      while (throwsIter < throws.length){
        // frames 1 to 9, 10 is a special case
        if (currentFrame.value > 0 && currentFrame.value < 10){
          // throw 1, need to check for strike
          if (currentRoll.value === 1){
            firstRollLoad = throws[throwsIter]
            if (!validateThrow(firstRollLoad, remainingPinsLoad)){
              newGame()
              return
            }
            throwsIter++
            // handle strike
            if (firstRollLoad === 10){
              currentFrame.value++
              continue
            }
            // not a strike, update remaining pins
            else {
              remainingPinsLoad = 10 - firstRollLoad
              currentRoll.value++
            }
          }
          // throw 2, no explicit need to check spare here, only needs to be validated since spare check is handled in calculateScore
          else {
            secondRollLoad = throws[throwsIter]
            if (!validateThrow(secondRollLoad, remainingPinsLoad)){
              newGame()
              return
            }
            throwsIter++
            firstRollLoad = null
            currentRoll.value = 1
            currentFrame.value++
            remainingPinsLoad = 10
          }
        }
        // tenth frame, special case since you can have three throws
        else if (currentFrame.value === 10){
          // first throw, need to check for strike
          if (currentRoll.value === 1){
            firstRollLoad = throws[throwsIter]
            if (!validateThrow(firstRollLoad, remainingPinsLoad)){
              newGame()
              return
            }
            throwsIter++
            currentRoll.value++
            // handle strike
            if (firstRollLoad !== 10){
              remainingPinsLoad = 10 - firstRollLoad
            }
            else {
              remainingPinsLoad = 10
            }
            continue
          }
          // second throw, need to check for strike or spare, so we can make sure a potential third throw is valid
          else if (currentRoll.value === 2){
            secondRollLoad = throws[throwsIter]
            if (!validateThrow(secondRollLoad, remainingPinsLoad)){
              newGame()
              return
            }
            throwsIter++
            // first throw was a strike
            if (firstRollLoad === 10){
              // handle second throw strike
              if (secondRollLoad === 10){
                currentRoll.value++
                continue
              }
              // handle second throw non-strike
              remainingPinsLoad = remainingPinsLoad - secondRollLoad
              currentRoll.value++
              continue
            }
            // handle second roll spare, special case since we have to reset pins for throw 3
            if (secondRollLoad === remainingPinsLoad){
              currentRoll.value++
              remainingPinsLoad = 10
              continue
            }
            // if throw 1 is not a strike and throw 2 is not a spare, end the game
            else{
              // if there is somehow extra data, game has been tampered with, purge and restart the game
              if (throwsIter !== throws.length){
                newGame()
                return
              }
              isEndOfGame.value = true
              break
            }
          }
          // third throw
          else if (currentRoll.value === 3){
            thirdRollLoad = throws[throwsIter]
            throwsIter++
            if (!validateThrow(thirdRollLoad, remainingPinsLoad)){
              newGame()
              return
            }
            if (throwsIter !== throws.length){
              newGame()
              return
            }
            isEndOfGame.value = true
            break
          }
        }
      }
      // update component-level state variables to pick up where this function left off
      remainingPins.value = remainingPinsLoad
      pins.value.length = 0
      for (let i = 1; i <= remainingPins.value; i++){
        pins.value.push(i)
      }
      firstRoll = firstRollLoad
      secondRoll = secondRollLoad
      // run calculateScore so we can have displayable frame data
      const scoreJSON = calculateScore(throws)
      if (!scoreJSON.isValid || scoreJSON.frames === null){
      // if validation in calculateScore fails, purge and restart the game
        newGame()
        return
      }
      else {
        frames.value = scoreJSON.frames
        total.value = scoreJSON.total
      }
    }
  }
</script>