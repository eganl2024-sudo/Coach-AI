import * as React from 'react'
import { cn } from '@/lib/utils'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      'flex h-12 w-full rounded-xl border-2 border-gray-200 bg-white px-4 text-base text-gray-900 placeholder:text-gray-400 focus:border-green-500 focus:outline-none transition-colors',
      className,
    )}
    {...props}
  />
))
Input.displayName = 'Input'

export { Input }
