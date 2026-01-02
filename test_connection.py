#!/usr/bin/env python3
"""
Script de teste de conexão com o banco de dados Azure SQL
Execute: python test_connection.py
"""
import asyncio
import sys
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine

# Verificar dependências antes de importar
try:
    import aioodbc
    import pyodbc
except ImportError as e:
    print("=" * 60)
    print("❌ DEPENDÊNCIA FALTANDO")
    print("=" * 60)
    print(f"Erro: {e}")
    print()
    print("🔧 Para instalar as dependências, execute:")
    print("   pip install aioodbc pyodbc")
    print()
    print("Ou instale todas as dependências do projeto:")
    print("   pip install -r requirements.txt")
    print()
    sys.exit(1)

from core.config import settings


def get_master_connection_string(conn_str: str) -> str:
    """Converte a string de conexão para usar o banco 'master'"""
    # Substituir o nome do banco por 'master'
    if "/" in conn_str:
        parts = conn_str.split("/", 1)
        if len(parts) == 2:
            # Pegar tudo antes do nome do banco e depois dos parâmetros
            base_part = parts[0]
            rest = parts[1]
            # Encontrar onde começam os parâmetros (?)
            if "?" in rest:
                params = rest.split("?", 1)[1]
                return f"{base_part}/master?{params}"
            else:
                return f"{base_part}/master"
    return conn_str.replace(settings.SQL_DATABASE, "master").replace("skillsync-db", "master")


async def test_connection():
    """Testa a conexão com o banco de dados"""
    print("🔌 Testando conexão com o banco de dados...")
    
    conn_str = settings.sql_connection_string
    # Debug: mostrar string de conexão (ocultando senha)
    if "@" in conn_str:
        display_str = conn_str.split("@")[0].split(":")[0] + ":****@" + "@".join(conn_str.split("@")[1:])
    else:
        display_str = conn_str
    print(f"📋 String de conexão: {display_str}")
    
    test_engine = None
    
    try:
        print("🔧 Criando engine...")
        test_engine = create_async_engine(
            conn_str,
            pool_size=1,
            max_overflow=0,
            pool_timeout=30,
            echo=False
        )
        print("✓ Engine criado")
        
        print("🔌 Tentando conectar...")
        async with test_engine.begin() as conn:
            print("✓ Conexão estabelecida, executando query...")
            # Executar query simples para testar
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
            print("✓ Query executada com sucesso")
            
            print("✅ CONEXÃO OK!")
            return True
            
    except SQLAlchemyError as e:
        error_msg = str(e)
        print(f"❌ Erro SQLAlchemy: {error_msg[:200]}")
        
        # Tentar conectar ao master se o banco não existir
        if "4060" in error_msg or "Cannot open database" in error_msg:
            print("⚠️  Banco não encontrado, testando conexão com servidor...")
            try:
                master_conn_str = get_master_connection_string(conn_str)
                print(f"📋 String master: {master_conn_str.split('@')[0].split(':')[0] + ':****@' + '@'.join(master_conn_str.split('@')[1:])}")
                
                print("🔧 Criando engine master...")
                master_engine = create_async_engine(
                    master_conn_str,
                    pool_size=1,
                    max_overflow=0,
                    pool_timeout=30,
                    echo=False
                )
                print("✓ Engine master criado")
                
                print("🔌 Tentando conectar ao master...")
                async with master_engine.begin() as conn:
                    print("✓ Conexão master estabelecida")
                    await conn.execute(text("SELECT 1"))
                    print("✓ Query master executada")
                
                await master_engine.dispose()
                print("✅ CONEXÃO COM SERVIDOR OK! (mas o banco especificado não existe)")
                return False
            except Exception as master_error:
                print(f"❌ Erro ao conectar ao master: {master_error}")
                import traceback
                traceback.print_exc()
        
        print("❌ ERRO NA CONEXÃO")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if test_engine:
            try:
                await test_engine.dispose()
            except:
                pass


async def main():
    """Função principal"""
    try:
        success = await test_connection()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠ Teste interrompido")
        return 1
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

