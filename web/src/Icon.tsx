export function Icon({name,size=18}:{name:string;size?:number}){
 const paths:Record<string,React.ReactNode>={
 history:<><path d="M3 11a9 9 0 1 1 2 7M3 4v7h7"/><path d="M12 7v5l3 2"/></>,
 help:<><circle cx="12" cy="12" r="9"/><path d="M9 9a3 3 0 0 1 6 0c0 2-3 2-3 4m0 3v.1"/></>,
 print:<><path d="M6 8V3h12v5M6 17H3V9h18v8h-3M6 14h12v7H6zM17 11h1"/></>,
 trash:<><path d="M4 6h16M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7m4-7v7"/></>,
 arrow:<><path d="M4 12h15M13 6l6 6-6 6"/></>,back:<><path d="M20 12H5m6-6-6 6 6 6"/></>,
 sun:<><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></>,
 moon:<path d="M20 15.5A8.5 8.5 0 0 1 8.5 4a8.5 8.5 0 1 0 11.5 11.5Z"/>,
 check:<path d="m5 12 4 4L19 6"/>,plus:<path d="M12 5v14M5 12h14"/>,
 folder:<path d="M3 7V5h6l2 2h10v13H3V7Z"/>,copy:<><rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V3H3v13h5"/></>,
 refresh:<><path d="M20 10a8 8 0 1 0-2 8M20 3v7h-7"/></>,close:<path d="m6 6 12 12M18 6 6 18"/>,
 settings:<><path d="M4 7h16M4 17h16"/><circle cx="9" cy="7" r="2"/><circle cx="15" cy="17" r="2"/></>,
 export:<><path d="M12 3v12m-4-4 4 4 4-4M4 16v5h16v-5"/></>,
 spark:<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z"/>,
 note:<><path d="M5 3h10l4 4v14H5V3Z"/><path d="M15 3v5h4M8 12h8m-8 4h6"/></>};
 return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]||paths.note}</svg>;
}
