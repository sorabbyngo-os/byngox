use crate::MemoryStore;

pub struct MemoryRetrieval;

impl MemoryRetrieval {
    pub fn search(
        store: &MemoryStore,
        user: &str,
        query: &str,
    ) -> Vec<String> {

        let query = query.to_lowercase();

        store
            .retrieve(user)
            .into_iter()
            .filter(|memory| {
                memory
                    .to_lowercase()
                    .contains(&query)
            })
            .collect()
    }
}
