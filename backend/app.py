from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc

app = Flask(__name__)
CORS(app)  

# Configuração da conexão com o banco de dados VTEX
conn = pyodbc.connect('Driver=/opt/homebrew/lib/libmsodbcsql.17.dylib;'
                      'Server=vtex.database.windows.net;'
                      'Database=VTEX;'
                      'UID=vtex;'
                      'PWD=97TpxyD^5M/Tp+&P;')

@app.route('/get_orders', methods=['GET'])
def get_orders():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = """
    SELECT 
        Seller.seller,
        COUNT(CASE WHEN [Order].Status = 'Faturado' THEN [Order].OrderId ELSE NULL END) AS CountFaturado
    FROM [Order]
    LEFT JOIN Seller ON [Order].OrderId = Seller.OrderId
    WHERE CAST([Order].DataFaturamento AS DATE) BETWEEN ? AND ?
    GROUP BY Seller.seller;
    """

    cursor = conn.cursor()
    cursor.execute(query, (start_date, end_date))
    result = cursor.fetchall()

    # Formatação do resultado para JSON
    data = [{'seller': row[0], 'count_faturado': row[1]} for row in result]

    return jsonify(data)

# Tratamento de erros para garantir que o backend retorne JSON em caso de erro
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)