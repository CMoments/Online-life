import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUserStore = defineStore('user', () => {
  const role = ref(localStorage.getItem('role') || '');
  
  function setRole(newRole) {
    role.value = newRole;
    if (newRole) {
      localStorage.setItem('role', newRole);
    } else {
      localStorage.removeItem('role');
    }
  }

  function clearUserData() {
    role.value = '';
    localStorage.removeItem('role');
    localStorage.removeItem('token');
  }

  return {
    role,
    setRole,
    clearUserData
  };
}); 