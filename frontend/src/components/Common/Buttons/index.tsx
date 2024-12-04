import React from 'react';

interface ButtonProps {
  text: string;
  type?: 'button' | 'submit' | 'reset';
  classname:string;
}

const Button: React.FC<ButtonProps> = ({ text, type = 'button',classname}) => {
  return (
    <button
      type={type}
      className={`w-full  bg-blue-500 text-white font-medium py-2 px-4 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 ${classname} `}
    >
      {text}
    </button>
  );
};

export default Button;
