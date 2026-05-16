import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Downloads from "./pages/Downloads.jsx";
import Home from "./pages/Home.jsx";
import Pipeline from "./pages/Pipeline.jsx";
import Preview from "./pages/Preview.jsx";
import Audit from "./pages/Audit.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="pipeline/:bookId" element={<Pipeline />} />
        <Route path="preview/:bookId" element={<Preview />} />
        <Route path="downloads/:bookId" element={<Downloads />} />
        <Route path="audit" element={<Audit />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
