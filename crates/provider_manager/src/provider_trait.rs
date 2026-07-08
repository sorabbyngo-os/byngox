use std::error::Error;

pub trait Provider {

    fn generate(
        &self,
        prompt: &str,
    ) -> Result<String, Box<dyn Error>>;

}
