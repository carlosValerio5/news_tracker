import React from 'react'

export const ButtonType = {
    PRIMARY: 'PRIMARY', 
    SECONDARY: 'SECONDARY',
} as const;

type ButtonType = keyof typeof ButtonType;

interface RegisterButtonProps {
    type?: ButtonType,
    text?: string
}

function RegisterButton({type = ButtonType.PRIMARY, text='Register'} : RegisterButtonProps) {
  return (
      <button className={`ml-3 bg-black text-white ${type === ButtonType.SECONDARY ? 'text-sm p-2.5' : 'text-md p-3'} rounded-sm border-2 hover:bg-white hover:border-black hover:text-black`}>
        {text}
      </button>
  )
}

export default RegisterButton