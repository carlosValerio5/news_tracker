export const ButtonType = {
    PRIMARY: 'PRIMARY', 
    SECONDARY: 'SECONDARY',
} as const;

type ButtonType = keyof typeof ButtonType;

interface RegisterButtonProps {
    type?: ButtonType,
    text?: string,
    className?: string,
}

function RegisterButton({type = ButtonType.PRIMARY, text='Register', className}: RegisterButtonProps) {
  return (
      <button className={`bg-black text-white ${type === ButtonType.SECONDARY ? 'text-sm p-2.5' : 'text-md p-3'} rounded-sm border-2 hover:bg-white hover:border-black hover:text-black ${className}`}>
        {text}
      </button>
  )
}

export default RegisterButton