import React from "react";

type InputFields={
    label:string;
    name:string;
    type:string;
    step?:string;
    placeholder?:string;
    required?: boolean;
    disabled?:boolean;
}


const InputField:React.FC<InputFields>=({label,name,type,placeholder,required,disabled=false,step})=>{
    return (<div className="py-2">
        <label htmlFor={name} className="block text-sm font-medium  mb-1">
        {label}
      </label>
      <input
        type={type}
        name={name}
        id={name}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        step={step}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-black"
      />
    </div>)
}



export default InputField;