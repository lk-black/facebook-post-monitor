import React, { useState } from "react";
import styled from "styled-components";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${({ theme }) => theme.colors.background};
`;
const Card = styled.div`
  background: ${({ theme }) => theme.colors.card};
  padding: 2.5rem 2rem;
  border-radius: ${({ theme }) => theme.borderRadius};
  box-shadow: 0 2px 16px rgba(0,0,0,0.04);
  width: 100%;
  max-width: 350px;
`;
const Title = styled.h2`
  margin-bottom: 1.5rem;
  font-weight: 600;
  font-size: 1.5rem;
  text-align: center;
`;
const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 8px;
  font-size: 1rem;
  background: #fafbfc;
`;
const Button = styled.button`
  width: 100%;
  padding: 0.75rem;
  background: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.5rem;
  transition: background 0.2s;
  &:hover {
    background: #1746a2;
  }
`;
const Error = styled.div`
  color: ${({ theme }) => theme.colors.error};
  margin-bottom: 1rem;
  text-align: center;
  font-size: 0.95rem;
`;
const Footer = styled.div`
  text-align: center;
  margin-top: 1rem;
  font-size: 0.95rem;
`;

const API_URL = "https://facebook-post-monitor.onrender.com";

const RegisterPage: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await axios.post(`${API_URL}/register`, { username, password });
      localStorage.setItem("token", res.data.access_token);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.error || "Erro ao registrar");
    }
  };

  return (
    <Container>
      <Card>
        <Title>Criar Conta</Title>
        {error && <Error>{error}</Error>}
        <form onSubmit={handleRegister}>
          <Input
            type="email"
            placeholder="E-mail"
            value={username}
            onChange={e => setUsername(e.target.value)}
            required
          />
          <Input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
          />
          <Button type="submit">Cadastrar</Button>
        </form>
        <Footer>
          Já tem conta? <Link to="/login">Entrar</Link>
        </Footer>
      </Card>
    </Container>
  );
};

export default RegisterPage;
