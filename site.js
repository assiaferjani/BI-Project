'use strict';
const annual=[{year:2020,articles:33566,change:null},{year:2021,articles:37160,change:10.7072633022},{year:2022,articles:40536,change:9.0850376749},{year:2023,articles:51037,change:25.9053680679},{year:2024,articles:67321,change:31.9062640829}];
const fmt=new Intl.NumberFormat('fr-FR');
for(const row of annual){
 const selector=document.createElement('button');selector.textContent=row.year;selector.type='button';selector.dataset.year=row.year;selector.setAttribute('aria-pressed','false');selector.addEventListener('click',()=>selectYear(row.year));document.querySelector('#years').append(selector);
 const wrapper=document.createElement('div');wrapper.className='bar';const bar=document.createElement('button');bar.type='button';bar.style.height=`${row.articles/67321*100}%`;bar.dataset.year=row.year;bar.setAttribute('aria-label',`${row.year} : ${fmt.format(row.articles)} articles`);bar.title=`${row.year} : ${fmt.format(row.articles)} articles`;bar.addEventListener('click',()=>selectYear(row.year));const label=document.createElement('span');label.textContent=row.year;wrapper.append(bar,label);document.querySelector('#bars').append(wrapper);
}
function selectYear(year){const row=annual.find(r=>r.year===year);document.querySelector('#annual-count').textContent=fmt.format(row.articles);document.querySelector('#annual-label').textContent=`articles déposés en ${year}`;document.querySelector('#annual-growth').textContent=row.change===null?'Variation non calculable dans la période':`+${row.change.toFixed(2).replace('.',',')} % par rapport à ${year-1}`;document.querySelectorAll('[data-year]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.year)===year)));}
selectYear(2024);
const dialog=document.querySelector('#viewer'),picture=document.querySelector('#viewer-image');
document.querySelectorAll('[data-image]').forEach(a=>a.addEventListener('click',e=>{if(typeof dialog.showModal!=='function')return;e.preventDefault();picture.src=a.dataset.image;picture.alt=a.querySelector('img').alt;dialog.showModal();}));
document.querySelector('#close-viewer').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
