'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { AlertCircle, Shield, X } from 'lucide-react'

interface EmergencyOverrideProps {
  onHalt: (reason: string) => Promise<void>
  onResume: (reason: string) => Promise<void>
  systemStatus: 'normal' | 'halted' | 'degraded'
}

export function EmergencyOverride({ onHalt, onResume, systemStatus }: EmergencyOverrideProps) {
  const [showDialog, setShowDialog] = useState(false)
  const [reason, setReason] = useState('')
  const [loading, setLoading] = useState(false)
  const [overrideError, setOverrideError] = useState<string | null>(null)
  const dialogRef = useRef<HTMLDivElement>(null)
  const triggerButtonRef = useRef<HTMLButtonElement>(null)

  const closeDialog = useCallback(() => {
    setShowDialog(false)
    setReason('')
    setOverrideError(null)
    if (triggerButtonRef.current) {
      triggerButtonRef.current.focus()
    }
  }, [])

  // Effect to manage focus within the dialog and close on Escape key
  useEffect(() => {
    if (!showDialog) return

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeDialog()
      } else if (event.key === 'Tab' && dialogRef.current) {
        const focusableElements = dialogRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        ) as NodeListOf<HTMLElement>
        const firstElement = focusableElements[0]
        const lastElement = focusableElements[focusableElements.length - 1]

        if (event.shiftKey) { // Tab backwards
          if (document.activeElement === firstElement) {
            lastElement.focus()
            event.preventDefault()
          }
        } else { // Tab forwards
          if (document.activeElement === lastElement) {
            firstElement.focus()
            event.preventDefault()
          }
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    // Set initial focus to the textarea when dialog opens
    const textarea = dialogRef.current?.querySelector('textarea')
    if (textarea) {
      textarea.focus()
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [showDialog, closeDialog])

  const handleOverride = async () => {
    setOverrideError(null)
    if (!reason || reason.length < 10) {
      setOverrideError('Please provide a detailed reason (at least 10 characters)')
      return
    }

    setLoading(true)
    try {
      if (systemStatus === 'halted') {
        await onResume(reason)
      } else {
        await onHalt(reason)
      }
      closeDialog()
    } catch (error) {
      console.error('Override error:', error)
      setOverrideError('Failed to execute override command. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="fixed bottom-4 right-4 z-50">
        <button
          ref={triggerButtonRef}
          onClick={() => setShowDialog(true)}
          className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all transform hover:scale-105 ${
            systemStatus === 'halted'
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-red-600 hover:bg-red-700 text-white'
          }`}
          aria-label={systemStatus === 'halted' ? 'Resume System Operations' : 'Initiate Emergency Halt'}
        >
          {systemStatus === 'halted' ? (
            <>
              <Shield className="w-5 h-5" />
              RESUME SYSTEM
            </>
          ) : (
            <>
              <AlertCircle className="w-5 h-5" />
              EMERGENCY HALT
            </>
          )}
        </button>
      </div>

      {showDialog && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          role="dialog"
          aria-modal="true"
          aria-labelledby="override-dialog-title"
          aria-describedby="override-dialog-description"
          ref={dialogRef}
        >
          <div className="bg-gray-800 p-6 rounded-lg max-w-md w-full relative">
            <button
              onClick={closeDialog}
              className="absolute top-3 right-3 text-gray-400 hover:text-white"
              aria-label="Close dialog"
            >
              <X className="w-6 h-6" />
            </button>
            <h2 id="override-dialog-title" className="text-xl font-bold mb-4 text-white">
              {systemStatus === 'halted' ? 'Resume System Operations' : 'Emergency System Halt'}
            </h2>
            
            <p id="override-dialog-description" className="text-gray-300 mb-4">
              {systemStatus === 'halted'
                ? 'This will resume all AI agent operations. Please provide a reason for the resume.'
                : 'This will immediately halt all AI agent operations. Please provide a reason for the emergency halt.'}
            </p>

            {overrideError && (
              <div className="bg-red-900 text-red-200 p-3 rounded-lg mb-4 text-sm" role="alert" aria-live="assertive">
                {overrideError}
              </div>
            )}

            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Enter reason (minimum 10 characters)..."
              className="w-full p-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none resize-y"
              aria-required="true"
              aria-invalid={reason.length < 10 && reason.length > 0 ? "true" : "false"}
              aria-describedby={reason.length < 10 && reason.length > 0 ? "reason-error" : undefined}
              rows={4}
            />
            {reason.length < 10 && reason.length > 0 && (
              <p id="reason-error" className="text-red-400 text-xs mt-1">
                Reason must be at least 10 characters.
              </p>
            )}

            <div className="flex gap-3 mt-4">
              <button
                onClick={closeDialog}
                className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                disabled={loading}
                aria-label="Cancel and close dialog"
              >
                Cancel
              </button>
              <button
                onClick={handleOverride}
                className={`flex-1 px-4 py-2 rounded-lg font-semibold transition-colors ${
                  systemStatus === 'halted'
                    ? 'bg-green-600 hover:bg-green-700 text-white'
                    : 'bg-red-600 hover:bg-red-700 text-white'
                } disabled:opacity-50`}
                disabled={loading || reason.length < 10}
                aria-busy={loading ? "true" : "false"}
                aria-label={loading ? (systemStatus === 'halted' ? 'Resuming system...' : 'Halting system...') : (systemStatus === 'halted' ? 'Resume System' : 'Halt System')}
              >
                {loading ? 'Processing...' : systemStatus === 'halted' ? 'Resume' : 'Halt System'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}