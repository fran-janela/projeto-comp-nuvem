# Projeto CompNuvem

## Instalação:

Para poder utilizar esta aplicação deverá possuir o python **3.10** instalado em sua máquina.

Depois deve criar um ambiente python virtual, para garantir que as bibliotecas para este programa estejam devidamente intaladas

Ative o ambiente virtual e utilize o arquivo `requirements.txt` para instalar as bibliotecas necessárias para o funcionamento do código

Além disso, o programa se baseia na utilização do CLI da terraform, portanto, também é necessário instalar o `Terraform`. Para isso, siga o tutorial neste [link](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)

## Preparação:

Antes de começar, deve configurar o arquivo `.env` com as variáveis indicadas no exemplo `.sample.env` com seus respectivos valores referentes à conta com Acesso de Administrador à sua AWS. **Muito cuidado com essas informações**, mantenha-as no arquivo `.env`.

## Iniciar:

Com a **Instalação** e a **Preparação** feitas, para iniciar o programa basta iniciar o arquivo `main.py` com o comando:

```
python3 main.py
```

--------------------

## Roteiro

Caso queira saber como funciona a aplicação ou esteja interessado em desenvolver uma aplicação para construção de infraestrutura com código, siga o roteiro neste [link](https://fran-janela.github.io/roteiro-proj-CompNuvem/)


--------------------

## Rúbrica:

- [x] Conceito C+ **feito**: A infraestrutura de rede é criada, o usuário consegue criar *Security Groups*, Instâncias com mais de 5 hosts, atrelar *Security Groups* a instâncias e criar usuários. Consegue deletar instâncias, *Security Groups* e usuários. E consegue listar Instâncias, Security Groups e Usuários.

- [x] Conceito B+ **feito**: Consegue adicionar regras aos *Security Groups*, consegue adicionar ou remover Restrições de Usuários e consegue criar infraestrutura em mais de uma região, assim como desfazer todas as ações.

- [x] Conceito A+ **feito**: O usuário consegue criar HA para um servidor Web;

A requisição quanto ao roteiro(tutorial) está no link na aba de **Roteiro**
