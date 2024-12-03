"use client";
import Button from "@/components/Common/Buttons";
import InputField from "@/components/Common/Inputs";
import TableComponent from "@/components/Common/Table";
import axios from "axios";
import { useState } from "react";


export default function Similarity(){
    const [data,setData]=useState<any[]>([]);
    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault(); 
        const formData = new FormData(event.currentTarget); 
        const data = Object.fromEntries(formData);
        console.log(data); 
        getSimilarityData(data);
    };
    const getSimilarityData=(data:any)=>{
    axios.get(`${process.env.NEXT_PUBLIC_API_URL}/similarity/commonprefixsuffix?name=${data?.name}&title=${data?.title}&meta=${data?.meta}`).then((data)=>{
        console.log(data);
        console.log(data.data.result)
        setData(data?.data?.result);
    }).catch((err)=>{
        console.log(err);
    })
    }
    return (
        <>
        <h1>
            dewdes  
            <form className="max-w-lg mx-auto mt-10 text-white shadow-md rounded-lg p-6"
      onSubmit={handleSubmit}
      >
        <InputField label="Name" type="text" name="name" placeholder="Enter Name" required />
        <InputField label="Title " step="0.01" type="number" name="title" placeholder="Enter title (In float)" required />
        <InputField label="Meta" step="0.01" type="number" name="meta" placeholder="Enter meta (In float)" required />
        <Button text="Submit" type="submit" classname="my-2 " /> 
        </form>
        </h1>

        {data && <TableComponent apiData={data} />}
        </>
    )
}