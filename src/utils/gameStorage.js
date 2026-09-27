/**
 * Loads a partial game from localStorage, if it exists.
 * @returns {number[]|null} - Partial throws array if it exists, null if not.
 */
export function loadPartialGame(){
    const partialGame = localStorage.getItem('throws')
    if (partialGame === null) return null
    return JSON.parse(partialGame)
}

/**
 * Saves a partial game to localStorage.
 * @param {number[]} throwsArray - The current game's partial throws array.
 */
export function savePartialGame(throwsArray){
    localStorage.setItem('throws', JSON.stringify(throwsArray))
}

/**
 * Clears a partial game from localStorage.
 */
export function clearPartialGame(){
    localStorage.removeItem('throws')
}