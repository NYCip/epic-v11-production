'use client'

import { useState } from 'react'
import { AlertCircle, Shield } from 'lucide-react'

interface EmergencyOverrideProps {
  onHalt: (reason: string) => Promise<void>
  onResume: (reason: string) => Promise<void>
  systemStatus: 'normal' | 'halted' | 'degraded'
}

export function EmergencyOverride({ onHalt, onResume, systemStatus }: EmergencyOverrideProps) {
  const [showDialog, setShowDialog] = useState(false)
  const [reason, setReason] = useState('')
  const [loading, setLoading] = useState(false)

  const handleOverride = async () => {
    if (!reason || reason.length < 10) {
      alert('Please provide a detailed reason (at least 10 characters)')
      return
    }

    setLoading(true)
    try {
      if (systemStatus === 'halted') {
        await onResume(reason)
      } else {
        await onHalt(reason)
      }
      setShowDialog(false)
      setReason('')
    } catch (error) {
      console.error('Override error:', error)
      alert('Failed to execute override command')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setShowDialog(true)}
          className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all transform hover:scale-105 ${
            systemStatus === 'halted'
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-red-600 hover:bg-red-700 text-white'
          }`}
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg max-w-md w-full">
            <h2 className="text-xl font-bold mb-4 text-white">
              {systemStatus === 'halted' ? 'Resume System Operations' : 'Emergency System Halt'}
            </h2>
            
            <p className="text-gray-300 mb-4">
              {systemStatus === 'halted'
                ? 'This will resume all AI agent operations. Please provide a reason for the resume.'
                : 'This will immediately halt all AI agent operations. Please provide a reason for the emergency halt.'}
            </p>

            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Enter reason (minimum 10 characters)..."
              className="w-full p-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
              rows={4}
            />

            <div className="flex gap-3 mt-4">
              <button
                onClick={() => {
                  setShowDialog(false)
                  setReason('')
                }}
                className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                disabled={loading}
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