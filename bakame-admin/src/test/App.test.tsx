import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '../App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    // Check if the app renders some content
    expect(document.body).toBeTruthy()
  })

  it('contains BAKAME text', () => {
    render(<App />)
    // Look for BAKAME text in the document
    const bakameElements = screen.queryAllByText(/BAKAME/i)
    expect(bakameElements.length).toBeGreaterThan(0)
  })
})