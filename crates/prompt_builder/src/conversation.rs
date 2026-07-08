use context::{Message, Role};

pub struct ConversationFormatter;

impl ConversationFormatter {
    pub fn format(messages: &[Message]) -> String {
        let mut output = String::new();

        for message in messages {
            let role = match message.role {
                Role::System => "System",
                Role::User => "User",
                Role::Assistant => "Assistant",
                Role::Tool => "Tool",
            };

            output.push_str(role);
            output.push_str(": ");
            output.push_str(&message.content);
            output.push('\n');
        }

        output
    }
}
