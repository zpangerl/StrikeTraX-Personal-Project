import { describe, it, expect } from 'vitest'
import { displayRoll, calculateScore, initializeFrames, validateThrow } from '../src/utils/scoring.js'

describe('validateThrow', () => {
  it('returns false for a non-number value', () => {
    expect(validateThrow('5', 10)).toBe(false)
  })

  it('returns false for a negative value', () => {
    expect(validateThrow(-1, 10)).toBe(false)
  })

  it('returns false for a value greater than the pins available', () => {
    expect(validateThrow(6, 5)).toBe(false)
  })

  it('returns true for a value within range', () => {
    expect(validateThrow(4, 10)).toBe(true)
  })

  it('returns true at the lower boundary (0)', () => {
    expect(validateThrow(0, 10)).toBe(true)
  })

  it('returns true at the upper boundary (equal to pins available)', () => {
    expect(validateThrow(7, 7)).toBe(true)
  })
})

describe('initializeFrames', () => {
  const frames = initializeFrames()

  it('returns 10 frames', () => {
    expect(frames.length).toBe(10)
  })

  it('numbers each frame 1 through 10', () => {
    frames.forEach((frame, i) => {
      expect(frame.frame).toBe(i + 1)
    })
  })

  it('initializes roll1, roll2, and currentTotal to null for frames 1-9', () => {
    for (let i = 0; i < 9; i++){
      expect(frames[i].roll1).toBeNull()
      expect(frames[i].roll2).toBeNull()
      expect(frames[i].currentTotal).toBeNull()
      expect(frames[i].roll3).toBeUndefined()
    }
  })

  it('initializes roll1, roll2, roll3, and currentTotal to null for frame 10', () => {
    const frame10 = frames[9]
    expect(frame10.roll1).toBeNull()
    expect(frame10.roll2).toBeNull()
    expect(frame10.roll3).toBeNull()
    expect(frame10.currentTotal).toBeNull()
  })
})

describe('displayRoll', () => {
  it('returns an empty string when the roll has not been thrown', () => {
    const frame = { frame: 1, roll1: null, roll2: null, currentTotal: null }
    expect(displayRoll(frame, 1)).toBe('')
  })

  it('returns X for a strike on roll1', () => {
    const frame = { frame: 1, roll1: 10, roll2: null, currentTotal: null }
    expect(displayRoll(frame, 1)).toBe('X')
  })

  it('returns X for a strike on roll2 (frame 10, second-ball strike)', () => {
    const frame = { frame: 10, roll1: 10, roll2: 10, roll3: null, currentTotal: null }
    expect(displayRoll(frame, 2)).toBe('X')
  })

  it('returns / for a spare on roll2', () => {
    const frame = { frame: 1, roll1: 6, roll2: 4, currentTotal: null }
    expect(displayRoll(frame, 2)).toBe('/')
  })

  it('returns the raw value on roll2 when it does not complete a spare', () => {
    const frame = { frame: 1, roll1: 6, roll2: 3, currentTotal: 9 }
    expect(displayRoll(frame, 2)).toBe(3)
  })

  it('does not misread roll2 as a spare when roll1 was already a strike', () => {
    const frame = { frame: 10, roll1: 10, roll2: 0, roll3: null, currentTotal: null }
    expect(displayRoll(frame, 2)).toBe(0)
  })

  it('returns / for a spare on roll3 (frame 10 bonus)', () => {
    const frame = { frame: 10, roll1: 0, roll2: 7, roll3: 3, currentTotal: null }
    expect(displayRoll(frame, 3)).toBe('/')
  })

  it('returns the raw value on roll3 when it does not complete a spare', () => {
    const frame = { frame: 10, roll1: 0, roll2: 7, roll3: 2, currentTotal: 9 }
    expect(displayRoll(frame, 3)).toBe(2)
  })

  it('does not misread roll3 as a spare when roll2 was already a strike', () => {
    const frame = { frame: 10, roll1: 10, roll2: 10, roll3: 5, currentTotal: null }
    expect(displayRoll(frame, 3)).toBe(5)
  })

  it('returns the raw value for a plain, unresolved roll1', () => {
    const frame = { frame: 1, roll1: 6, roll2: null, currentTotal: null }
    expect(displayRoll(frame, 1)).toBe(6)
  })
})

describe('calculateScore - validation', () => {
  it('flags the game invalid when a throw is negative', () => {
    const result = calculateScore([-1])
    expect(result.isValid).toBe(false)
  })

  it('flags the game invalid when a throw exceeds the pins remaining', () => {
    const result = calculateScore([6, 5])
    expect(result.isValid).toBe(false)
  })

  it('flags the game invalid when a throw is not a number', () => {
    const result = calculateScore(['strike'])
    expect(result.isValid).toBe(false)
  })
})

describe('calculateScore - strikes in frames 1-9', () => {
  it('leaves the total hidden and only records roll1 when the bonus throws are not yet available', () => {
    const result = calculateScore([10])
    expect(result.isValid).toBe(true)
    expect(result.frames[0].roll1).toBe(10)
    expect(result.frames[0].currentTotal).toBeNull()
    expect(result.currFrame).toBe(1)
    expect(result.currThrow).toBe(1)
  })

  it('records the next throw for display purposes when only one bonus throw is available', () => {
    const result = calculateScore([10, 5])
    expect(result.frames[0].roll1).toBe(10)
    expect(result.frames[0].currentTotal).toBeNull()
    expect(result.frames[1].roll1).toBe(5)
  })

  it('resolves the strike and reveals the total once both bonus throws are available', () => {
    const result = calculateScore([10, 3, 4])
    expect(result.frames[0].roll1).toBe(10)
    expect(result.frames[0].currentTotal).toBe(17)
    expect(result.currFrame).toBe(3)
  })
})

describe('calculateScore - spares in frames 1-9', () => {
  it('leaves the total hidden and null when the bonus throw is not yet available', () => {
    const result = calculateScore([6, 4])
    expect(result.isValid).toBe(true)
    expect(result.frames[0].roll1).toBe(6)
    expect(result.frames[0].roll2).toBe(4)
    expect(result.frames[0].currentTotal).toBeNull()
  })

  it('resolves the spare and reveals the total once the bonus throw is available', () => {
    const result = calculateScore([6, 4, 5])
    expect(result.frames[0].currentTotal).toBe(15)
    expect(result.currFrame).toBe(2)
  })
})

describe('calculateScore - open frames in frames 1-9', () => {
  it('hides the total after the first throw of an open frame', () => {
    const result = calculateScore([3])
    expect(result.frames[0].roll1).toBe(3)
    expect(result.frames[0].currentTotal).toBeNull()
    expect(result.total).toBe(3)
  })

  it('reveals the total once both throws of an open frame are complete', () => {
    const result = calculateScore([3, 4])
    expect(result.frames[0].roll1).toBe(3)
    expect(result.frames[0].roll2).toBe(4)
    expect(result.frames[0].currentTotal).toBe(7)
    expect(result.currFrame).toBe(2)
    expect(result.currThrow).toBe(1)
  })
})

describe('calculateScore - frame 10', () => {
  // quick and easy way to "skip" to frame 10
  const nineOpenFrames = Array(18).fill(0)

  it('tracks a non-strike first throw', () => {
    const result = calculateScore([...nineOpenFrames, 5])
    expect(result.currFrame).toBe(10)
    expect(result.currThrow).toBe(2)
    expect(result.frames[9].roll1).toBe(5)
  })

  it('tracks a strike first throw', () => {
    const result = calculateScore([...nineOpenFrames, 10])
    expect(result.frames[9].roll1).toBe(10)
    expect(result.currThrow).toBe(2)
  })

  it('tracks a second-throw strike after a first-throw strike', () => {
    const result = calculateScore([...nineOpenFrames, 10, 10])
    expect(result.frames[9].roll1).toBe(10)
    expect(result.frames[9].roll2).toBe(10)
    expect(result.currThrow).toBe(3)
  })

  it('tracks a non-strike second throw after a first-throw strike', () => {
    const result = calculateScore([...nineOpenFrames, 10, 4])
    expect(result.frames[9].roll2).toBe(4)
    expect(result.currThrow).toBe(3)
  })

  it('tracks a second throw that completes a spare', () => {
    const result = calculateScore([...nineOpenFrames, 6, 4])
    expect(result.frames[9].roll1).toBe(6)
    expect(result.frames[9].roll2).toBe(4)
    expect(result.currThrow).toBe(3)
  })

  it('records an open 10th frame that does not earn a bonus throw', () => {
    const result = calculateScore([...nineOpenFrames, 6, 3])
    expect(result.isValid).toBe(true)
    expect(result.frames[9].roll1).toBe(6)
    expect(result.frames[9].roll2).toBe(3)
    expect(result.frames[9].currentTotal).toBe(9)
  })

  it('records a third throw following an earned bonus and reveals the total immediately', () => {
    const result = calculateScore([...nineOpenFrames, 10, 10, 10])
    expect(result.frames[9].roll1).toBe(10)
    expect(result.frames[9].roll2).toBe(10)
    expect(result.frames[9].roll3).toBe(10)
    expect(result.frames[9].currentTotal).toBe(30)
  })

  it('reveals frame 10 totals progressively, unlike frames 1-9', () => {
    const result = calculateScore([...nineOpenFrames, 10, 4])
    expect(result.frames[9].currentTotal).toBe(14)
  })
})

describe('calculateScore - full games', () => {
  it('scores a perfect game as 300', () => {
    // 12 strikes is a perfect game, quick way to fill throws array
    const result = calculateScore(Array(12).fill(10))
    expect(result.isValid).toBe(true)
    expect(result.total).toBe(300)
    expect(result.frames[9].currentTotal).toBe(300)
  })

  it('scores an all-gutter game as 0', () => {
    // 20 0s is a 0 score complete game, quick way to fill throws array
    const result = calculateScore(Array(20).fill(0))
    expect(result.isValid).toBe(true)
    expect(result.total).toBe(0)
    expect(result.frames[9].currentTotal).toBe(0)
  })

  it('scores a realistic mixed game correctly', () => {
    const throws = [5, 3, 3, 5, 10, 10, 1, 3, 4, 4, 5, 5, 6, 3, 6, 3, 5, 4]
    const result = calculateScore(throws)
    expect(result.isValid).toBe(true)
    expect(result.frames[0].currentTotal).toBe(8)
    expect(result.frames[1].currentTotal).toBe(16)
    expect(result.frames[9].currentTotal).toBe(result.total)
  })
})
