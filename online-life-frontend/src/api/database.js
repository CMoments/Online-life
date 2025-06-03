import request from './request';

// 获取所有表名
export const getAllTables = () => {
  return request({
    url: '/api/database/tables',
    method: 'get'
  });
};

// 获取指定表的数据
export const getTableData = (tableName, page = 1, perPage = 10) => {
  return request({
    url: `/api/database/table/${tableName}`,
    method: 'get',
    params: { page, per_page: perPage }
  });
};

// 获取表结构信息
export const getTableSchema = (tableName) => {
  return request({
    url: `/api/database/table/${tableName}/schema`,
    method: 'get'
  });
}; 