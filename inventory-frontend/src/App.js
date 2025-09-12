import {Products} from "./Components/Products";
import {BrowserRouter, Routes, Route} from 'react-router-dom';
import {ProductsCreate} from "./Components/ProductsCreate";
import {Orders} from "./Components/Orders";

function App() {
    return <BrowserRouter>
        <Routes>
            <Route path="/" element={<Products/>}/>
            <Route path="/create" element={<ProductsCreate/>}/>
            <Route path="/orders" element={<Orders/>}/>
        </Routes>
    </BrowserRouter>;
}

export default App;