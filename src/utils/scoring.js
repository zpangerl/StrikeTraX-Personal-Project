/**
 * Used as a utility file by Scoring.vue and History.vue so they can utilize functions for both live scoring
 * and reconstructing complete games.
 * 
 * Decoupled from any individual component's state so it can be used by either, or future, components
 */

/**
 * Determines what to display within a specific frame roll box.
 * @param {Object} frame - The frame object being checked.
 * @param {number} rollNum - Which roll within the frame to check (1, 2, or 3).
 * @returns {string|number} 'X' for a strike, '/' for a spare, '' if not yet thrown, or the raw value otherwise.
 */
export function displayRoll(frame, rollNum){
    const roll = frame[`roll${rollNum}`]
    if (roll === null) return ''
    if (roll === 10) return 'X'
    else if (rollNum === 2 && frame.roll1 + roll === 10 && frame.roll1 !== 10) return '/'
    else if (rollNum === 3 && frame.roll2 + roll === 10 && frame.roll2 !== 10) return '/'
    else return roll
}

/**
 * Takes a raw throw array and converts it into displayable frames.
 * Frames include all rolls and the score up to that frame, as long as all strikes and spares
 * have been resolved and/or both throws of the frame are complete.
 * Resolving a strike/spare means the next 2/1 throw(s), respectively, have been logged.
 * @param {number[]} throwsArray - The raw array of throws for the current state of the game.
 * @returns {Object} A JSON object containing the computed frames array, a validity flag, current throw/frame position, pins remaining, and the running total
 */
export function calculateScore(throwsArray){
  let throwsIter = 0
  let currentThrow = 1
  let currentFrame = 1
  let totalPinsThisFrame = 0
  let currentTotal = 0
  // create empty array of 10 frames
  const gameFrames = initializeFrames()
  // create base return JSON object
  const returnJSON = {
    frames: null,
    isValid: true,
    currThrow: 1,
    currFrame: 1,
    pinsLeft: 10,
    total: null
  }

  while (throwsIter < throwsArray.length){
    const nextThrow = throwsArray[throwsIter]
    if (!validateThrow(nextThrow, 10 - totalPinsThisFrame)){
      returnJSON.isValid = false
      return returnJSON
    }
    // if the current throw being processed is the first throw of a frame, is a strike, and is not in frame 10
    if (currentThrow === 1 && nextThrow === 10 && currentFrame !== 10){
      // check to see if next two throws exist to resolve strike
      // if they don't exist, we need to exit scoring for now instead of continuing
      // only used during live play, history will process full games, but live play requires partial games
      if (throwsIter + 2 >= throwsArray.length) {
        // check to see if the next throw exists, only for display purposes
        // without this, the throw immediately after a strike will not display until after the next throw
        if (throwsArray[throwsIter + 1] !== undefined){
          gameFrames[currentFrame].roll1 = throwsArray[throwsIter + 1]
        }
        // if the next two throws don't exist, populate return JSON and return
        gameFrames[currentFrame - 1].roll1 = nextThrow
        // populate return JSON with current state
        returnJSON.frames = gameFrames
        returnJSON.currThrow = currentThrow
        returnJSON.currFrame = currentFrame
        returnJSON.pinsLeft = 10 - totalPinsThisFrame
        returnJSON.total = currentTotal
        return returnJSON
      }
      // if the 2 throws after the strike exist, update pin count for the frame
      totalPinsThisFrame += nextThrow
      // update current total, applying the next two throws to the current strike per bowling rules
      currentTotal += nextThrow
      currentTotal += throwsArray[throwsIter + 1]
      currentTotal += throwsArray[throwsIter + 2]
      gameFrames[currentFrame - 1].roll1 = nextThrow
      // update current total of current frame, since strike is fully resolved
      gameFrames[currentFrame - 1].currentTotal = currentTotal
      currentThrow++
    }
    // if the current throw is the second throw of a frame, is a spare, and is not in frame 10
    else if (currentThrow === 2 && nextThrow === (10 - totalPinsThisFrame) && currentFrame !== 10){
      // check to see if next throw exists to resolve spare
      // if it doesn't exist, we need to exit scoring for now instead of continuing
      // only used during live play, history will process full games, but live play requires partial games
      if (throwsIter + 1 >= throwsArray.length) {
        // if next throw doesn't exist, populate return JSON and return
        gameFrames[currentFrame - 1].roll2 = nextThrow
        // explicitly set the current frame's current total to null, since the spare hasn't been resolved yet
        gameFrames[currentFrame - 1].currentTotal = null
        // populate return JSON with current state
        returnJSON.frames = gameFrames
        returnJSON.currThrow = currentThrow
        returnJSON.currFrame = currentFrame
        returnJSON.pinsLeft = 10 - totalPinsThisFrame
        returnJSON.total = currentTotal
        return returnJSON
      }
      // if the throw after the spare exists, update pin count for the frame
      totalPinsThisFrame += nextThrow
      // update current total, applying the next throw to the current spare per bowling rules
      currentTotal += nextThrow
      currentTotal += throwsArray[throwsIter + 1]
      gameFrames[currentFrame - 1].roll2 = nextThrow
      // update current total of current frame, since spare is fully resolved
      gameFrames[currentFrame - 1].currentTotal = currentTotal
      currentThrow++
    }
    // if the frame is specifically frame 10
    // frame 10 is a special case, three potential throws instead of 2 if you get a strike/spare
    // additionally, strikes and spares made in frame 10 do not apply double the next throw(s)
    else if (currentFrame === 10){
      // first throw
      if (currentThrow === 1){
        // if the throw isn't a strike, update pin counter
        if (nextThrow !== 10){
          totalPinsThisFrame += nextThrow
        }
        // if it is, we can just leave it at 0
        else totalPinsThisFrame = 0
      }
      // second throw
      else if (currentThrow === 2){
        // check if the first throw was a strike, if it is we don't have to check if this is a spare
        if (gameFrames[currentFrame - 1].roll1 === 10){
          // if this throw is also a strike, set pin counter to 0
          if (nextThrow === 10){
            totalPinsThisFrame = 0
          }
          // if this throw isn't a strike, update pin counter
          else {
            totalPinsThisFrame += nextThrow
          }
        }
        // if the first throw was not a strike
        else{
          // need to check if this throw is a spare, if it is set pin count to 0
          if (nextThrow === (10 - totalPinsThisFrame)){
            totalPinsThisFrame = 0
          }
          // if not, the game is over
          else{
            // check for extra, invalid throws
            if (throwsIter + 1 !== throwsArray.length){
              returnJSON.isValid = false
              return returnJSON
            }
            // set total pins to 10, since the frame at this point is complete
            totalPinsThisFrame = 10
            currentTotal += nextThrow
            gameFrames[currentFrame - 1].roll2 = nextThrow
            gameFrames[currentFrame - 1].currentTotal = currentTotal
            currentThrow++
            // game is over, break
            break
          }
        }
      }
      // optional third throw, if strike or spare have been made in the first two throws
      else if (currentThrow === 3){
        // check for extra, invalid throws
        if (throwsIter + 1 !== throwsArray.length){
          returnJSON.isValid = false
          return returnJSON
        }
        currentTotal += nextThrow
        gameFrames[currentFrame - 1].roll3 = nextThrow
        // update current total of current frame
        gameFrames[currentFrame - 1].currentTotal = currentTotal
        currentThrow++
        // game is over, break
        break
      }
      // for any throw in frame 10 that isn't the last throw of the game
      currentTotal += nextThrow
      gameFrames[currentFrame - 1][`roll${currentThrow}`] = nextThrow
      // we don't need to worry about waiting to display the current total, strikes and spares made in frame 10 don't apply bonuses
      gameFrames[currentFrame - 1].currentTotal = currentTotal
      currentThrow++
    }
    // if not a strike, spare, or frame 10
    else{
      totalPinsThisFrame += nextThrow
      currentTotal += nextThrow
      gameFrames[currentFrame - 1][`roll${currentThrow}`] = nextThrow
      // if the current throw isn't the first, frame is finished, so update the current total of the current frame
      // if the frame isn't finished, we don't display the current frame's score yet
      // this will also keep the first throw after a strike from displaying a score before the strike is resolved
      if (currentThrow != 1){
        gameFrames[currentFrame - 1].currentTotal = currentTotal
      }
      currentThrow++
    }
    // if currentThrow is more than 2 or pin counter is 10, frame is over
    // frame 10 is a special case, handled separately
    if (((currentThrow > 2 || totalPinsThisFrame === 10) && currentFrame !== 10)){
      // reset currentThrow for next frame
      currentThrow = 1
      currentFrame++
      totalPinsThisFrame = 0
    }
    throwsIter++
  }
  // populate and return JSON object
  returnJSON.total = currentTotal
  returnJSON.currThrow = currentThrow
  returnJSON.currFrame = currentFrame
  returnJSON.pinsLeft = 10 - totalPinsThisFrame
  returnJSON.frames = gameFrames
  return returnJSON
}

/**
 * Creates and returns an array of empty frames
 * @returns {Object[]} - A 10 length array of empty frame objects
 */
export function initializeFrames(){
  const framesArr = []
  for (let i = 0; i < 9; i++){
    framesArr.push({ frame: i + 1, roll1: null, roll2: null, currentTotal: null })
  }
  framesArr.push({ frame: 10, roll1: null, roll2: null, roll3: null, currentTotal: null })
  return framesArr
}

/**
 * Validates a given throw from the game, given the throw and the remaining pins in the current frame
 * @param {number} throwVal - The value to be validated
 * @param {number} pinsVal  - The remaining pins in the current frame
 * @returns {boolean} - True if throw is valid, false if not
 */
export function validateThrow(throwVal, pinsVal){
  if (typeof throwVal !== 'number' || throwVal < 0 || throwVal > pinsVal){
    return false
  }
  else return true
}