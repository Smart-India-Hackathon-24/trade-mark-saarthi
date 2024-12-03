"use client";
import Button from "@/components/Common/Buttons";
import InputField from "@/components/Common/Inputs";

export default function Registration(){
    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault(); 
        const formData = new FormData(event.currentTarget); 
        const data = Object.fromEntries(formData);
        console.log(data); 
    };
    return (
        <>
         <div className="max-w-lg mx-auto mt-10 text-white shadow-md rounded-lg p-6">
      <h1 className="text-2xl font-bold text-center mb-6">Newspaper Registration</h1>
      <form 
      onSubmit={handleSubmit}
      >
        <InputField label="Title" type="text" name="title" placeholder="Enter title" required disabled={true}/>
        <InputField label="Publisher Name" type="text" name="publisher" placeholder="Enter publisher's name" required />
        <InputField label="Email Address" type="email" name="email" placeholder="Enter email address" required
        />
        <InputField label="Contact Number" type="tel" name="contact" placeholder="Enter contact number" required />

        {/* <SelectField
          label="Publication Frequency"
          name="frequency"
          options={['Daily', 'Weekly', 'Monthly']}
          required
        />
        <SelectField
          label="Language"
          name="language"
          options={['English', 'Hindi', 'Spanish']}
          required
        />
        */}
        <Button text="Register" type="submit" classname="my-2 " /> 
      </form>
    </div>
        </>
    )
}